from django import forms
from aplication.attention.models import HorarioAtencion

class ScheduleAttentionForm(forms.ModelForm):
    class Meta:
        model = HorarioAtencion
        fields = ["dia_semana", "hora_inicio", "hora_fin", "intervalo_desde", "intervalo_hasta", "activo"]

        widgets = {
            "dia_semana": forms.Select(
                attrs={
                    "placeholder": "Seleccione el día de la semana",
                    "id": "id_dia_semana",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                }
            ),
            "hora_inicio": forms.TimeInput(
                attrs={
                    "placeholder": "Ingrese la hora de inicio",
                    "id": "id_hora_inicio",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                },
                format='%H:%M'
            ),
            "hora_fin": forms.TimeInput(
                attrs={
                    "placeholder": "Ingrese la hora de fin",
                    "id": "id_hora_fin",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                },
                format='%H:%M'
            ),
            "intervalo_desde": forms.TimeInput(
                attrs={
                    "placeholder": "Ingrese el intervalo desde",
                    "id": "id_intervalo_desde",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                },
                format='%H:%M'
            ),
            "intervalo_hasta": forms.TimeInput(
                attrs={
                    "placeholder": "Ingrese el intervalo hasta",
                    "id": "id_intervalo_hasta",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                },
                format='%H:%M'
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "mt-1 block px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
        }
        labels = {
            "dia_semana": "Día de la Semana",
            "hora_inicio": "Hora de Inicio",
            "hora_fin": "Hora de Fin",
            "intervalo_desde": "Intervalo desde",
            "intervalo_hasta": "Intervalo hasta",
            "activo": "Activo",
        }
        def clean(self):
            cleaned_data = super().clean()
            hora_inicio = cleaned_data.get("hora_inicio")
            hora_fin = cleaned_data.get("hora_fin")
            intervalo_desde = cleaned_data.get("intervalo_desde")
            intervalo_hasta = cleaned_data.get("intervalo_hasta")

            if hora_inicio and hora_fin and hora_inicio >= hora_fin:
                self.add_error("hora_inicio", "La hora de inicio debe ser menor que la hora de fin.")
            
            if intervalo_desde and intervalo_hasta and intervalo_desde >= intervalo_hasta:
                self.add_error("intervalo_desde", "El intervalo de descanso es inválido.")
            
            if hora_inicio and intervalo_desde and intervalo_hasta and hora_fin:
                if not (hora_inicio <= intervalo_desde < intervalo_hasta <= hora_fin):
                    self.add_error("intervalo_desde", "El intervalo debe estar dentro del horario de atención.")
            
            return cleaned_data