from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from aplication.security.models import User, Menu, Module, GroupModulePermission
from django.forms import ModelForm

class ProfileUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'dni', 'phone', 'direction', 'image']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'username': 'Nombre de usuario',
            'dni': 'Cédula o RUC',
            'phone': 'Teléfono',
            'direction': 'Dirección',
            'image': 'Imagen de perfil',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'direction': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Introduce una dirección de correo válida.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class MenuForm(ModelForm):
    class Meta:
        model = Menu
        fields = "__all__"
        
class ModuloForm(ModelForm):
    class Meta:
        model = Module
        fields = "__all__"
        
class GroupModulePermissionForm(ModelForm):
    class Meta:
        model = GroupModulePermission
        fields = "__all__"
        