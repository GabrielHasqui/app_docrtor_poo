from django import forms
from aplication.attention.models import ServiciosAdicionales

class AdditionalServicesForm(forms.ModelForm):
    class Meta:
        model = ServiciosAdicionales
        fields = ['nombre_servicio', 'costo_servicio', 'descripcion', 'activo']
        
        error_messages = {
            'nombre_servicio': {
                'required': "El nombre del servicio es requerido"
            },
            'costo_servicio': {
                'required': "El costo del servicio es requerido"
            },
            'descripcion': {
                'required': "La descripción del servicio es requerida"
            }
        }
        
        widgets = {
            'nombre_servicio': forms.TextInput(
                attrs={
                    "placeholder": "Ingrese nombre del servicio",
                    "id": "id_nombre_servicio",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                }
            ),
            'costo_servicio': forms.NumberInput(
                attrs={
                    "placeholder": "Ingrese costo del servicio",
                    "id": "id_costo_servicio",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    "placeholder": "Ingrese descripción del servicio",
                    "id": "id_descripcion",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 pr-12 dark:bg-principal dark:border-gray-600 dark:placeholder-gray-400 dark:text-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light",
                    "rows": 3,
                }
            ),
            'activo': forms.CheckboxInput(
                attrs={
                    "id": "id_activo",
                    "class": "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
                }
            ),
        }

    def clean_costo_servicio(self):
        costo = self.cleaned_data.get('costo_servicio')
        if costo is None:
            raise forms.ValidationError("El costo del servicio es requerido")
        if costo <= 0:
            raise forms.ValidationError("El costo del servicio debe ser mayor que 0")
        return costo