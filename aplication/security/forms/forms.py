from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UpdateProfileForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    new_password2 = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'dni', 'phone', 'email', 'image', 
            'direction'
        ]
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "type": "file",
                    "id": "dropzone-file",
                    "class": "hidden",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['email'].initial = self.instance.email
            self.fields['phone'].initial = self.instance.phone
            self.fields['dni'].initial = self.instance.dni
            self.fields['direction'].initial = self.instance.direction
            self.fields['image'].initial = self.instance.image
