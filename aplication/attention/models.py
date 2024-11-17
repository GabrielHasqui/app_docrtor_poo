from django.db import models
from aplication.core.models import *
from doctor.const import CITA_CHOICES, DIA_SEMANA_CHOICES, EXAMEN_CHOICES
from django.core.exceptions import ValidationError


# Modelo que representa los días y horas de atención de un doctor.
# Incluye los días de la semana, la hora de inicio y la hora de fin de la atención.
class HorarioAtencion(models.Model):
    dia_semana = models.CharField(max_length=10, choices=DIA_SEMANA_CHOICES, verbose_name="Día de la Semana", unique=True)
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    intervalo_desde = models.TimeField(verbose_name="Intervalo desde")
    intervalo_hasta = models.TimeField(verbose_name="Intervalo Hasta")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def clean(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser menor que la hora de fin.")
        if self.intervalo_desde >= self.intervalo_hasta:
            raise ValidationError("El intervalo de descanso es inválido.")
        if not (self.hora_inicio <= self.intervalo_desde < self.intervalo_hasta <= self.hora_fin):
            raise ValidationError("El intervalo debe estar dentro del horario de atención.")

    def __str__(self):
        return f"{self.dia_semana}: {self.hora_inicio} - {self.hora_fin} (Descanso: {self.intervalo_desde} - {self.intervalo_hasta})"

    class Meta:
        verbose_name = "Horario de Atención del Doctor"
        verbose_name_plural = "Horarios de Atención de los Doctores"


# Modelo para citas médicas
class CitaMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente", related_name="pacientes_citas")
    fecha = models.DateField(verbose_name="Fecha de la Cita")
    hora_cita = models.TimeField(verbose_name="Hora de la Cita")
    estado = models.CharField(max_length=1, choices=CITA_CHOICES, verbose_name="Estado de la Cita")

    def __str__(self):
        return f"Cita {self.paciente} el {self.fecha} a las {self.hora_cita}"

    class Meta:
        ordering = ['fecha', 'hora_cita']
        indexes = [models.Index(fields=['fecha', 'hora_cita'], name='idx_fecha_hora')]
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"


# Modelo que representa la cabecera de una atención médica.
# Contiene la información general del paciente, diagnóstico, motivo de consulta y tratamiento.
class Atencion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, verbose_name="Paciente", related_name="doctores_atencion")
    fecha_atencion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Atención")
    presion_arterial = models.CharField(max_length=20, null=True, blank=True, verbose_name="Presión Arterial")
    pulso = models.IntegerField(null=True, blank=True, verbose_name="Pulso (ppm)")
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Temperatura (°C)")
    frecuencia_respiratoria = models.IntegerField(null=True, blank=True, verbose_name="Frecuencia Respiratoria(rpm)")
    saturacion_oxigeno = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Saturación de Oxígeno (%)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Altura (m)")
    motivo_consulta = models.TextField(verbose_name="Motivo de Consulta")
    sintomas = models.TextField(verbose_name="Sintomas")
    tratamiento = models.TextField(verbose_name="Plan de Tratamiento")
    diagnostico = models.ManyToManyField(Diagnostico, verbose_name="Diagnósticos", related_name="diagnosticos_atencion")
    examen_fisico = models.TextField(null=True, blank=True, verbose_name="Examen Físico")
    examenes_enviados = models.TextField(null=True, blank=True, verbose_name="Examenes enviados")
    comentario_adicional = models.TextField(null=True, blank=True, verbose_name="Comentario")

    @property
    def get_diagnosticos(self):
        return " - ".join([c.descripcion for c in self.diagnostico.all().order_by('descripcion')])

    @property
    def calcular_imc(self):
        """Calcula el Índice de Masa Corporal (IMC) basado en el peso y la altura."""
        if self.peso and self.altura and self.altura > 0:
            return round(float(self.peso) / (float(self.altura) ** 2), 2)
        else:
            return None

    def __str__(self):
        return f"Atención de {self.paciente} el {self.fecha_atencion}"

    class Meta:
        ordering = ['-fecha_atencion']
        verbose_name = "Atención"
        verbose_name_plural = "Atenciones"


# Modelo que representa el detalle de una atención médica.
# Relaciona cada atención con los medicamentos recetados y su cantidad.
class DetalleAtencion(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE, verbose_name="Cabecera de Atención", related_name="atenciones")
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, verbose_name="Medicamento", related_name="medicamentos")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    prescripcion = models.TextField(verbose_name="Prescripción")
    duracion_tratamiento = models.PositiveIntegerField(verbose_name="Duración del Tratamiento (días)", null=True, blank=True)

    def __str__(self):
        return f"Detalle de {self.medicamento} para {self.atencion}"

    class Meta:
        ordering = ['atencion']
        verbose_name = "Detalle de Atención"
        verbose_name_plural = "Detalles de Atención"


# Modelo que representa un servicio adicional ofrecido durante una atención médica.
# Puede incluir exámenes, procedimientos, o cualquier otro servicio.
class ServiciosAdicionales(models.Model):
    nombre_servicio = models.CharField(max_length=255, verbose_name="Nombre del Servicio")
    costo_servicio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo del Servicio")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción del Servicio")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return self.nombre_servicio

    class Meta:
        ordering = ['nombre_servicio']
        verbose_name = "Servicio Adicional"
        verbose_name_plural = "Servicios Adicionales"


# Modelo que representa los costos asociados a una atención médica,
# incluyendo consulta, servicios adicionales (exámenes, procedimientos), y otros costos.
class CostosAtencion(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.PROTECT, verbose_name="Atención", related_name="costos_atencion")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total", default=0.00)
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name="Fecha Pago")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return f"{self.atencion} - Total: {self.total}"

    class Meta:
        ordering = ['-fecha_pago']
        verbose_name = "Costo de Atención"
        verbose_name_plural = "Costos de Atención"


class CostoAtencionDetalle(models.Model):
    costo_atencion = models.ForeignKey(CostosAtencion, on_delete=models.PROTECT, verbose_name="Costo Atención", related_name="costos_atenciones")
    servicios_adicionales = models.ForeignKey(ServiciosAdicionales, on_delete=models.PROTECT, verbose_name="Servicios Adicionales", related_name="servicios_adicionales")
    costo_servicio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo del Servicio")

    def __str__(self):
        return f"{self.servicios_adicionales} Costo: {self.costo_servicio}"

    class Meta:
        verbose_name = "Costo detalle Atención"
        verbose_name_plural = "Costos detalles Atención"
