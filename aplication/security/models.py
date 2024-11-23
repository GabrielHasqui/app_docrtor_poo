import json
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from crum import get_current_request
from django.db import models
from django.forms import model_to_dict
import logging
import datetime
from datetime import date

logger = logging.getLogger(__name__)


class Menu(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=150, unique=True)
    icon = models.CharField(verbose_name='Icono', max_length=100)

    def __str__(self):
        return self.name

    def get_model_to_dict(self):
        return model_to_dict(self)

    def get_icon(self):
        return self.icon if self.icon else 'bi bi-calendar-x-fill'

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['-name']

class Module(models.Model):
    url = models.CharField(verbose_name='Url', max_length=100, unique=True)
    name = models.CharField(verbose_name='Nombre', max_length=100)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT, verbose_name='Menu')
    description = models.CharField(verbose_name='Descripción', max_length=200, null=True, blank=True)
    icon = models.CharField(verbose_name='Icono', max_length=100, null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Es activo', default=True)
    permissions = models.ManyToManyField(Permission, verbose_name='Permisos', blank=True)

    def __str__(self):
        return '{} [{}]'.format(self.name, self.url)

    def get_model_to_dict(self):
        return model_to_dict(self)

    def get_icon(self):
        return self.icon if self.icon else 'bi bi-x-octagon'

    class Meta:
        verbose_name = 'Modulo'
        verbose_name_plural = 'Modulos'
        ordering = ('-name',)

class GroupModulePermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Grupo')
    module = models.ForeignKey(Module, on_delete=models.PROTECT, verbose_name='Modulo')
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return f"{self.module.name} - {self.group.name}"

    @staticmethod
    def get_group_module_permission_active_list(group_id):
        return GroupModulePermission.objects.select_related('module', 'module__menu').filter(
            group_id=group_id, module__is_active=True)

    class Meta:
        verbose_name = 'Grupo modulo permiso'
        verbose_name_plural = 'Grupos modulos Permisos'
        ordering = ('-id',)

class User(AbstractUser):
    dni = models.CharField(verbose_name='Cédula o RUC', max_length=13, blank=True, null=True)
    image = models.ImageField(verbose_name='Archive image', upload_to='users/', max_length=1024, blank=True, null=True)
    email = models.EmailField('Email', unique=True)
    direction = models.CharField('Direccion', max_length=200, blank=True, null=True)
    phone = models.CharField('Telefono', max_length=50, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        permissions = (
            ("change_userprofile", "Cambiar perfil Usuario"),
            ("change_userpassword", "Cambiar password Usuario"),
        )

    def __str__(self):
        return self.username

    @property
    def edad(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None
    
    def __str__(self):
        return '{}'.format(self.username)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_groups(self):
        return self.groups.all()

    def get_short_name(self):
        return self.username

    def get_group_session(self):
        request = get_current_request()
        logger.debug(f"Request actual: {request}")
        if request is None:
            logger.error("No se encontró un request actual.")
            return None
        group_id = request.session.get('group_id')
        if group_id:
            logger.debug(f"Group ID encontrado: {group_id}")
            return Group.objects.get(pk=group_id)
        logger.warning("No se encontró un group_id en la sesión.")
        return None

    def set_group_session(self):
        request = get_current_request()

        if 'group' not in request.session:

            groups = request.user.groups.all().order_by('id')

            if groups.exists():
                request.session['group'] = groups.first()
                request.session['group_id'] = request.session['group'].id
    
    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/usuario_anonimo.png'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class AuditUser(models.Model):
    TIPOS_ACCIONES = (
        ('A', 'A'),   # Adicion
        ('M', 'M'),   # Modificacion
        ('E', 'E')    # Eliminacion
    )
    usuario = models.ForeignKey(User, verbose_name='Usuario',on_delete=models.PROTECT)
    tabla = models.CharField(max_length=100, verbose_name='Tabla')
    registroid = models.IntegerField(verbose_name='Registro Id')
    accion = models.CharField(choices=TIPOS_ACCIONES, max_length=10, verbose_name='Accion')
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    estacion = models.CharField(max_length=100, verbose_name='Estacion')

    def __str__(self):
        return "{} - {} [{}]".format(self.usuario.username, self.tabla, self.accion)

    class Meta:
        verbose_name = 'Auditoria Usuario '
        verbose_name_plural = 'Auditorias Usuarios'
        ordering = ('-fecha', 'hora')
        
