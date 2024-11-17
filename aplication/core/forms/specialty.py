from django.forms import ModelForm, ValidationError
from django import forms
from aplication.core.models import Especialidad

class SpecialtyForm(ModelForm):
    class Meta:
        model = Especialidad
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese nombre de la especialidad",
                    "id": "id_nombre",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                }
            ),
            "descripcion": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese descripción",
                    "id": "id_descripcion",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                }
            ),
        }
        labels = {
            "nombre": "Nombre de la Especialidad",
            "descripcion": "Descripción",
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if not nombre or len(nombre) < 1:
            raise ValidationError("El nombre de la especialidad debe tener al menos 1 carácter.")
        return nombre.upper()

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion")
        if not descripcion or len(descripcion) < 1:
            raise ValidationError("La descripción debe tener al menos 1 carácter.")
        return descripcion.upper()