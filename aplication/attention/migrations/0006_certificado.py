# Generated by Django 5.1.2 on 2024-11-19 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attention', '0005_alter_horarioatencion_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_certificado', models.CharField(choices=[('MEDICO', 'Certificado Médico'), ('REPOSO', 'Certificado de Reposo'), ('DISCAPACIDAD', 'Certificado de Discapacidad')], max_length=20, verbose_name='Tipo de Certificado')),
                ('fecha_emision', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Emisión')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('archivo_pdf', models.FileField(upload_to='certificados/', verbose_name='Archivo PDF')),
                ('atencion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='attention.atencion', verbose_name='Atención')),
            ],
        ),
    ]
