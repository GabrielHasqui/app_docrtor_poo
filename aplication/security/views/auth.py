from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django .contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from aplication.security.views.forms import CustomUserCreationForm, ProfileUserCreationForm
from django.contrib import messages
from aplication.security.forms.forms import UpdateProfileForm
from django.db.models import Q

# # ----------------- Registro -----------------
def signup(request):
    data = {
        "title1": "IC - Registro",
        "title2": "Registro de Usuarios"
    }

    if request.method == "GET":
        form = CustomUserCreationForm()
        return render(request, "security/auth/signup.html", {"form": form, **data})

    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Registro exitoso! Por favor, inicia sesión.')
            return redirect("security:auth_login")
        else:
            error_messages = []
            for field in form:
                for error in field.errors:
                    error_messages.append(f"{field.label}: {error}")
            for error in form.non_field_errors():
                error_messages.append(error)
            data["errors"] = error_messages

            return render(request, "security/auth/signup.html", {"form": form, **data})

# # ----------------- Cerrar Sesion -----------------
@login_required
def signout(request):
    logout(request)
    return redirect("core:home")

# # ----------------- Iniciar Sesion -----------------
def signin(request):
    data = {
        "title1": "Login",
        "title2": "Inicio de Sesión"
    }
    if request.method == "GET":
        success_messages = messages.get_messages(request)
        return render(request, "security/auth/signin.html", {
            "form": AuthenticationForm(),
            "success_messages": success_messages,
            **data
        })
    elif request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # Aquí 'username' debe ser el campo 'email' en tu formulario
            password = form.cleaned_data['password']
            print(email, password)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                return redirect("core:home")  # Redireccionar a la URL deseada después del inicio de sesión
            else:
                return render(request, "security/auth/signin.html", {
                    "form": form,
                    "error": "El usuario o la contraseña son incorrectos",
                    **data
                })
        else:
            return render(request, "security/auth/signin.html", {
                "form": form,
                "error": "Datos inválidos",
                **data
            })

#--- view Profile ---#
@login_required
def profile_view(request):
    data = {
        "title1": "Perfil",
        "title2": "Perfil de Usuario"
    }
    return render(request, "security/auth/profile.html", data)

@login_required
def update_profile(request):
    data = {"title1": "IC - Actualizar Perfil", "title2": "Actualizar Perfil"}
    
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            current_password = form.cleaned_data.get('current_password')
            new_password1 = form.cleaned_data.get('new_password1')
            new_password2 = form.cleaned_data.get('new_password2')

            if current_password and new_password1 and new_password2:
                if not request.user.check_password(current_password):
                    messages.error(request, 'La contraseña actual es incorrecta.')
                elif new_password1 != new_password2:
                    messages.error(request, 'Las nuevas contraseñas no coinciden.')
                else:
                    request.user.set_password(new_password1)
                    update_session_auth_hash(request, request.user)
                    messages.success(request, '¡Tu contraseña ha sido actualizada exitosamente!')

            user.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('security:profile_view')
    else:
        form = UpdateProfileForm(instance=request.user)
    
    return render(request, 'security/auth/update_profile.html', {'form': form, **data})