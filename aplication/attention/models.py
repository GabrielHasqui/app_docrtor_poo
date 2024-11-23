from datetime import timezone
from decimal import Decimal
from django.db import models
from aplication.core.models import *
from doctor.const import CITA_CHOICES, DIA_SEMANA_CHOICES, EXAMEN_CHOICES
from django.core.exceptions import ValidationError
from django.db.models import Sum


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
    valor_consulta = models.DecimalField(
    max_digits=10, 
    decimal_places=2, 
    verbose_name="Valor de Consulta",
    default=0.00
    )
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

    def get_total_medicamentos(self):
        """Calcula el total de medicamentos recetados"""
        return self.medicamentos_recetados.aggregate(
            total=Sum(models.F('cantidad') * models.F('medicamento__precio'))
        )['total'] or Decimal('0.00')
    
    def get_total_examenes(self):
        """Calcula el total de exámenes realizados"""
        return self.examenes_realizados.aggregate(
            total=Sum('examen__precio')
        )['total'] or Decimal('0.00')

    def get_total_servicios(self):
        """Calcula el total de servicios adicionales"""
        return self.servicios_prestados.aggregate(
            total=Sum('servicio__costo_servicio')
        )['total'] or Decimal('0.00')

    def get_total_atencion(self):
        """Calcula el total general de la atención"""
        return (
            self.valor_consulta +
            self.get_total_medicamentos() +
            self.get_total_examenes() +
            self.get_total_servicios()
        )
    
    
    def __str__(self):
        return f"Atención de {self.paciente} el {self.fecha_atencion}"

    class Meta:
        ordering = ['-fecha_atencion']
        verbose_name = "Atención"
        verbose_name_plural = "Atenciones"

class DetalleAtencion(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE, verbose_name="Cabecera de Atención", related_name='medicamentos_recetados')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, verbose_name="Medicamento", related_name='prescripciones')
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    prescripcion = models.TextField(verbose_name="Prescripción")
    duracion_tratamiento = models.PositiveIntegerField(verbose_name="Duración del Tratamiento (días)", null=True, blank=True)

    @property
    def subtotal(self):
        return self.cantidad * self.medicamento.precio

    def __str__(self):
        return f"Detalle de {self.medicamento} para {self.atencion}"

    class Meta:
        ordering = ['atencion']
        verbose_name = "Detalle de Atención"
        verbose_name_plural = "Detalles de Atención"



class Examen(models.Model):
    tipo_examen = models.CharField(max_length=20, choices=EXAMEN_CHOICES, verbose_name="Tipo de Examen")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    
class DetalleExamen(models.Model):
    atencion = models.ForeignKey(
        Atencion, 
        on_delete=models.CASCADE, 
        related_name='examenes_realizados'
    )
    examen = models.ForeignKey(
        Examen, 
        on_delete=models.PROTECT,
        related_name='realizados'
    )
    resultado = models.TextField()
    fecha_realizacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Detalle de {self.examen} para {self.atencion}"

    class Meta:
        ordering = ['atencion']
        verbose_name = "Detalle de Examen"
        verbose_name_plural = "Detalles de Examen"

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

class ServicioAtencion(models.Model):
    """Nuevo modelo para relacionar servicios con atenciones"""
    atencion = models.ForeignKey(
        Atencion, 
        on_delete=models.CASCADE,
        related_name='servicios_prestados'
    )
    servicio = models.ForeignKey(
        ServiciosAdicionales,
        on_delete=models.PROTECT,
        related_name='prestaciones'
    )
    cantidad = models.PositiveIntegerField(default=1)
    
    @property
    def subtotal(self):
        return self.cantidad * self.servicio.costo_servicio





class Factura(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('EMITIDA', 'Emitida'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada')
    ]
    METODO_PAGO_CHOICES = [
            ('EFECTIVO', 'Efectivo'),
            ('PAYPAL', 'PayPal'),
        ]

    atencion = models.OneToOneField(
        'Atencion', 
        on_delete=models.PROTECT, 
        related_name='factura'
    )
    numero_factura = models.CharField(max_length=20, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='BORRADOR'
    )
    metodo_pago = models.CharField(
        max_length=20, 
        choices=METODO_PAGO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Método de Pago"
    )
    fecha_pago = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Pago"
    )
    referencia_pago = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Referencia de Pago"
    )

    def registrar_pago(self, metodo, referencia=None):
        """Registra el pago de la factura"""
        if self.estado != 'BORRADOR':
            raise ValueError("Solo se pueden pagar facturas en estado borrador")
            
        self.estado = 'PAGADA'
        self.metodo_pago = metodo
        self.fecha_pago = timezone.now()
        if referencia:
            self.referencia_pago = referencia
        self.save()
    def generar_detalles(self):
        """Genera los detalles de la factura basados en la atención"""
        # Limpiar detalles existentes
        self.detalles.all().delete()
        
        # Agregar consulta médica
        if self.atencion.valor_consulta > 0:
            DetalleFactura.objects.create(
                factura=self,
                tipo='CONSULTA',
                descripcion="Consulta médica",
                cantidad=1,
                precio_unitario=self.atencion.valor_consulta
            )

        # Agregar medicamentos
        for detalle in self.atencion.medicamentos_recetados.all():
            DetalleFactura.objects.create(
                factura=self,
                tipo='MEDICAMENTO',
                descripcion=f"Medicamento: {detalle.medicamento.nombre}",
                cantidad=detalle.cantidad,
                precio_unitario=detalle.medicamento.precio
            )

        # Agregar exámenes
        for examen in self.atencion.examenes_realizados.all():
            DetalleFactura.objects.create(
                factura=self,
                tipo='EXAMEN',
                descripcion=f"Examen: {examen.examen.tipo_examen}",
                cantidad=1,
                precio_unitario=examen.examen.precio
            )

        # Agregar servicios adicionales
        for servicio in self.atencion.servicios_prestados.all():
            DetalleFactura.objects.create(
                factura=self,
                tipo='SERVICIO',
                descripcion=f"Servicio: {servicio.servicio.nombre_servicio}",
                cantidad=servicio.cantidad,
                precio_unitario=servicio.servicio.costo_servicio
            )

        self.calcular_totales()

    def calcular_totales(self):
        """Calcula los totales de la factura"""
        self.subtotal = self.detalles.aggregate(
            total=Sum('subtotal')
        )['total'] or Decimal('0.00')
        self.iva = self.subtotal * Decimal('0.12')
        self.total = self.subtotal + self.iva
        self.save()

    def emitir(self):
        """Emite la factura cambiando su estado"""
        if self.estado == 'BORRADOR':
            self.estado = 'EMITIDA'
            self.save()

    def anular(self):
        """Anula la factura"""
        if self.estado in ['EMITIDA', 'PAGADA']:
            self.estado = 'ANULADA'
            self.save()

class DetalleFactura(models.Model):
    TIPO_CHOICES = [
        ('CONSULTA', 'Consulta'),
        ('MEDICAMENTO', 'Medicamento'),
        ('EXAMEN', 'Examen'),
        ('SERVICIO', 'Servicio Adicional')
    ]

    factura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE, 
        related_name='detalles'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        if not kwargs.get('skip_factura_update', False):
            self.factura.calcular_totales()

class Certificado(models.Model):
    TIPO_CHOICES = [
        ('MEDICO', 'Certificado Médico'),
        ('REPOSO', 'Certificado de Reposo'),
        ('DISCAPACIDAD', 'Certificado de Discapacidad')
    ]

    atencion = models.ForeignKey(Atencion, on_delete=models.PROTECT, verbose_name="Atención")
    tipo_certificado = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Certificado")
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    descripcion = models.TextField(verbose_name="Descripción")
    archivo_pdf = models.FileField(upload_to='certificados/', verbose_name="Archivo PDF")
    
    def __str__(self):
        return f"{self.tipo_certificado} - {self.atencion.paciente}"