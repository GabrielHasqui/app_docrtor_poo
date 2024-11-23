from django import forms
from django.forms import ModelForm
from aplication.attention.models import Examen

class ExamenForm(ModelForm):
    class Meta:
        model = Examen
        fields = ['tipo_examen', 'descripcion', 'precio']
        
        widgets = {
            "tipo_examen": forms.Select(
                attrs={
                    "class": "form-select shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
                    "id": "id_tipo_examen",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
                    "placeholder": "Ingrese la descripción del examen",
                    "rows": 4,
                    "id": "id_descripcion",
                }
            ),
            "precio": forms.NumberInput(
                attrs={
                    "class": "form-control shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500",
                    "placeholder": "Ingrese el precio del examen",
                    "step": "0.01",
                    "id": "id_precio",
                }
            ),
        }