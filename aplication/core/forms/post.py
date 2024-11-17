from django.forms import ModelForm, ValidationError
from django import forms
from aplication.core.models import Cargo

class CargoForm(ModelForm):
    class Meta:
        model = Cargo
        fields = ["nombre", "descripcion", "activo"]
        
        error_messages = {
            "nombre": {
                "unique": "Ya existe un cargo con este nombre",
            },
        }
        
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese nombre del cargo",
                    "id": "id_nombre",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                }
            ),
            "descripcion": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese descripción del cargo",
                    "id": "id_descripcion",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "mt-1 block px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if not nombre or len(nombre) < 3:
            raise ValidationError("El nombre del cargo debe tener al menos 3 caracteres.")
        return nombre.upper()