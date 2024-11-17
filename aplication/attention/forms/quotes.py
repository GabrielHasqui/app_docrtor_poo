from django import forms
from django.utils import timezone
from aplication.attention.models import CitaMedica, HorarioAtencion
from django.core.exceptions import ValidationError
import datetime


class QuoteForm(forms.ModelForm):
    class Meta:
        model = CitaMedica
    class Meta:
        model = CitaMedica
        fields = ['paciente', 'fecha', 'hora_cita', 'estado']
        
        error_messages = {
            'paciente': {
                'required': "El campo paciente es requerido"
            },
            'fecha': {
                'required': "El campo fecha es requerido"
            },
            'hora_cita': {
                'required': "El campo hora de la cita es requerido"
            },
            'estado': {
                'required': "El campo estado es requerido"
            }
        }
        
        widgets = {
            'paciente': forms.Select(
            attrs={
                "id": "id_paciente",
                "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
            }
            ),
            'fecha': forms.DateInput(
            attrs={
                "placeholder": "Ingrese fecha de la cita",
                "id": "id_fecha",
                "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                "type": "date",
                "min": datetime.date.today().strftime('%Y-%m-%d'),
            },
            format='%Y-%m-%d'
            ),
            'hora_cita': forms.TimeInput(
            attrs={
                "placeholder": "Ingrese hora de la cita",
                "id": "id_hora_cita",
                "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                "type": "time",
            },
            format='%H:%M'
            ),
            'estado': forms.Select(
            attrs={
                "id": "id_estado",
                "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
            }
            ),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            raise ValidationError("El campo fecha es requerido")
        if fecha <= datetime.date.today():
            raise ValidationError("La fecha debe ser posterior a la fecha actual")
        return fecha

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            raise ValidationError("El campo fecha es requerido")
        return fecha

    def clean_hora_cita(self):
        hora_cita = self.cleaned_data.get('hora_cita')
        if not hora_cita:
            raise ValidationError("El campo hora de la cita es requerido")
        return hora_cita