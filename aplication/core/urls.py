from django.urls import path
from aplication.core.views.home import HomeTemplateView
from aplication.core.views.patient import *
from aplication.core.views.blood_type import *
from aplication.core.views.specialty import *
from aplication.core.views.doctor import *
from aplication.core.views.post import *
from aplication.core.views.employee import *
from aplication.core.views.doctor import *
from aplication.core.views.medication_type import *
from aplication.core.views.brand_medicine import *
from aplication.core.views.medicine import *
from aplication.core.views.diagnosis import *
from aplication.core.views.auditUser import *
from aplication.core.views.statistics import *

app_name = 'core'

urlpatterns = [
  # ruta principal
  path('', HomeTemplateView.as_view(), name='home'),

  # rutas de pacientes
  path('patient_list/', PatientListView.as_view(), name="patient_list"),
  path('patient_create/', PatientCreateView.as_view(), name="patient_create"),
  path('patient_update/<int:pk>/', PatientUpdateView.as_view(), name='patient_update'),
  path('patient_delete/<int:pk>/', PatientDeleteView.as_view(), name='patient_delete'),
  path('patient_detail/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),

  # rutas de tipos de sangre
  path('blood_type_list/', BloodTypeListView.as_view(), name="blood_type_list"),
  path('blood_type_create/', BloodTypeCreateView.as_view(), name="blood_type_create"),
  path('blood_type_update/<int:pk>/', BloodTypeUpdateView.as_view(), name='blood_type_update'),
  path('blood_type_delete/<int:pk>/', BloodTypeDeleteView.as_view(), name='blood_type_delete'),
  path('blood_type_detail/<int:pk>/', BloodTypeDetailView.as_view(), name='blood_type_detail'),

  # rutas de especialidades
  path('specialty_list/', SpecialtyListView.as_view(), name="specialty_list"),
  path('specialty_create/', SpecialtyCreateView.as_view(), name="specialty_create"),
  path('specialty_update/<int:pk>/', SpecialtyUpdateView.as_view(), name='specialty_update'),
  path('specialty_delete/<int:pk>/', SpecialtyDeleteView.as_view(), name='specialty_delete'),
  path('specialty_detail/<int:pk>/', SpecialtyDetailView.as_view(), name='specialty_detail'),
  
  # rutas de doctores
  path('doctor_list/', DoctorListView.as_view(), name="doctor_list"),
  path('doctor_create/', DoctorCreateView.as_view(), name="doctor_create"),
  path('doctor_update/<int:pk>/', DoctorUpdateView.as_view(), name='doctor_update'),
  path('doctor_delete/<int:pk>/', DoctorDeleteView.as_view(), name='doctor_delete'),
  path('doctor_detail/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
  
  # rutas de cargos
  path('post_list/', PostListView.as_view(), name="post_list"),
  path('post_create/', PostCreateView.as_view(), name="post_create"),
  path('post_update/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
  path('post_delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
  path('post_detail/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
  
  # rutas de empleados
  path('employee_list/', EmployeeListView.as_view(), name="employee_list"),
  path('employee_create/', EmployeeCreateView.as_view(), name="employee_create"),
  path('employee_update/<int:pk>/', EmployeeUpdateView.as_view(), name='employee_update'),
  path('employee_delete/<int:pk>/', EmployeeDeleteView.as_view(), name='employee_delete'),
  path('employee_detail/<int:pk>/', EmployeeDetailView.as_view(), name='employee_detail'),
  
  # rutas de tipos de medicamentos
  path('medication_type_list/', MedicationTypeListView.as_view(), name="medication_type_list"),
  path('medication_type_create/', MedicationTypeCreateView.as_view(), name="medication_type_create"),
  path('medication_type_update/<int:pk>/', MedicationTypeUpdateView.as_view(), name='medication_type_update'),
  path('medication_type_delete/<int:pk>/', MedicationTypeDeleteView.as_view(), name='medication_type_delete'),
  path('medication_type_detail/<int:pk>/', MedicationTypeDetailView.as_view(), name='medication_type_detail'),
  
  # rutas de marcas de medicamentos
  path('brand_medicine_list/', BrandMedicineListView.as_view(), name="brand_medicine_list"),
  path('brand_medicine_create/', BrandMedicineCreateView.as_view(), name="brand_medicine_create"),
  path('brand_medicine_update/<int:pk>/', BrandMedicineUpdateView.as_view(), name='brand_medicine_update'),
  path('brand_medicine_delete/<int:pk>/', BrandMedicineDeleteView.as_view(), name='brand_medicine_delete'),
  path('brand_medicine_detail/<int:pk>/', BrandMedicineDetailView.as_view(), name='brand_medicine_detail'),
  
  # rutas de medicamentos
  path('medicine_list/', MedicineListView.as_view(), name="medicine_list"),
  path('medicine_create/', MedicineCreateView.as_view(), name="medicine_create"),
  path('medicine_update/<int:pk>/', MedicineUpdateView.as_view(), name='medicine_update'),
  path('medicine_delete/<int:pk>/', MedicineDeleteView.as_view(), name='medicine_delete'),
  path('medicine_detail/<int:pk>/', MedicineDetailView.as_view(), name='medicine_detail'),
  
  # rutas de diagnósticos
  path('diagnosis_list/', DiagnosisListView.as_view(), name="diagnosis_list"),
  path('diagnosis_create/', DiagnosisCreateView.as_view(), name="diagnosis_create"),
  path('diagnosis_update/<int:pk>/', DiagnosisUpdateView.as_view(), name='diagnosis_update'),
  path('diagnosis_delete/<int:pk>/', DiagnosisDeleteView.as_view(), name='diagnosis_delete'),
  path('diagnosis_detail/<int:pk>/', DiagnosisDetailView.as_view(), name='diagnosis_detail'),
  
  # rutas de auditoría
  path('audit_user_list/', AuditUserListView.as_view(), name="audit_user_list"),
  path('audit_user_detail/<int:pk>/', AuditUserDetailView.as_view(), name='audit_user_detail'),
  
  # rutas de estadísticas
  path('statistics/', VistaEstadisticas.as_view(), name='statistics'),
  
  
]
