from datetime import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg, Sum
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeekDay
from aplication.attention.models import CitaMedica, DetalleAtencion
from aplication.core.models import Paciente

class VistaEstadisticas(LoginRequiredMixin, TemplateView):
    template_name = 'core/statistics/statistics.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        año_actual = datetime.now().year
        total_citas = CitaMedica.objects.count()


        contexto.update({

            'title': 'Estadísticas',

            'año_actual': año_actual,

            'total_citas': total_citas,

            'total_pacientes': self._get_total_pacientes(),

            'citas_mensuales': list(self._get_citas_mensuales(año_actual)),

            'citas_por_estado': list(self._get_citas_por_estado()),

            'tasa_finalizacion': self._calcular_tasa_finalizacion(total_citas),

            'crecimiento_pacientes': list(self._get_crecimiento_pacientes()),

            'pacientes_por_genero': list(self._get_pacientes_por_genero()),

            'edad_promedio': self._get_edad_promedio(),

            'citas_por_dia': list(self._get_citas_por_dia()),

            'comparacion_citas': self._get_comparacion_citas(),

            'medicamentos_mas_recetados': list(self._get_medicamentos_mas_recetados())

        })
        return contexto

    @staticmethod
    def _get_total_pacientes():
        return Paciente.objects.count()

    @staticmethod
    def _get_medicamentos_mas_recetados(limit=10):
        return DetalleAtencion.objects.values(
            'medicamento__nombre'
        ).annotate(
            total_recetado=Sum('cantidad')
        ).order_by('-total_recetado')[:limit]

    @staticmethod
    def _get_citas_mensuales(año):
        return CitaMedica.objects.filter(
            fecha__year=año
        ).annotate(
            mes=ExtractMonth('fecha')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')

    @staticmethod
    def _get_citas_por_estado():
        return CitaMedica.objects.values('estado').annotate(total=Count('id'))

    @staticmethod
    def _calcular_tasa_finalizacion(total_citas):
        if not total_citas:
            return 0
        citas_completadas = CitaMedica.objects.filter(estado='R').count()
        return round((citas_completadas / total_citas * 100), 2)

    @staticmethod
    def _get_crecimiento_pacientes():
        return Paciente.objects.annotate(
            año=ExtractYear('fecha_nacimiento'),
            mes=ExtractMonth('fecha_nacimiento')
        ).values('año', 'mes').annotate(
            total=Count('id')
        ).order_by('año', 'mes')

    @staticmethod
    def _get_pacientes_por_genero():
        return Paciente.objects.values('sexo').annotate(total=Count('id'))

    @staticmethod
    def _get_edad_promedio():
        return round(Paciente.objects.annotate(
            edad=datetime.now().year - ExtractYear('fecha_nacimiento')
        ).aggregate(promedio=Avg('edad'))['promedio'] or 0, 1)

    @staticmethod
    def _get_citas_por_dia():
        return CitaMedica.objects.annotate(
            dia=ExtractWeekDay('fecha')
        ).values('dia').annotate(
            total=Count('id')
        ).order_by('dia')

    @staticmethod
    def _get_comparacion_citas():
        return {estado: CitaMedica.objects.filter(estado=estado).count() 
                for estado in ['R', 'C', 'P']}
