from django.urls import path

from aplication.attention.views.certificate import (CertificateCreateView,
                                                    CertificateDeleteView,
                                                    CertificateDetailView,
                                                    CertificateListView,
                                                    CertificatePDFView,
                                                    CertificateUpdateView)
from aplication.attention.views.clinical_record import (
    ClinicalRecordDetailView, ClinicalRecordListView, ImprimirHistorialClinico)
from aplication.attention.views.medical_attention import (AttentionCreateView,
                                                          AttentionDetailView,
                                                          AttentionListView,
                                                          AttentionUpdateView,
                                                          ExaminationCreateView, FacturaDetailView, InvoiceCreateView, payment_cancel, payment_success,
                                                          )
from aplication.attention.views.quotes import (QuoteCreateView,
                                               QuoteDeleteView,
                                               QuoteDetailView, QuoteListView,
                                               QuoteUpdateView)
from aplication.attention.views.ScheduleAttention import (
    ScheduleAttentionCreateView, ScheduleAttentionDeleteView,
    ScheduleAttentionDetailView, ScheduleAttentionListView,
    ScheduleAttentionUpdateView)
from aplication.attention.views.serviciosAdicionales import (
    ServiciosAdicionalesCreateView, ServiciosAdicionalesDeleteView,
    ServiciosAdicionalesDetailView, ServiciosAdicionalesListView,
    ServiciosAdicionalesUpdateView)
from aplication.attention.views.examination import ExaminationListView, ExaminationCreateView, ExaminationUpdateView, ExaminationDeleteView, ExaminationDetailView

app_name = "attention"  # define un espacio de nombre para la aplicacion

urlpatterns = [
    # rutas de atenciones
    path("attention_list/", AttentionListView.as_view(), name="attention_list"),
    path("attention_create/", AttentionCreateView.as_view(), name="attention_create"),
    path(
        "attention_update/<int:pk>/",
        AttentionUpdateView.as_view(),
        name="attention_update",
    ),
    path(
        "attention_detail/<int:pk>/",
        AttentionDetailView.as_view(),
        name="attention_detail",
    ),
    # rutas de horario de atencion
    path(
        "schedule_attention_list/",
        ScheduleAttentionListView.as_view(),
        name="schedule_attention_list",
    ),
    path(
        "schedule_attention_create/",
        ScheduleAttentionCreateView.as_view(),
        name="schedule_attention_create",
    ),
    path(
        "schedule_attention_update/<int:pk>/",
        ScheduleAttentionUpdateView.as_view(),
        name="schedule_attention_update",
    ),
    path(
        "schedule_attention_delete/<int:pk>/",
        ScheduleAttentionDeleteView.as_view(),
        name="schedule_attention_delete",
    ),
    path(
        "schedule_attention_detail/<int:pk>/",
        ScheduleAttentionDetailView.as_view(),
        name="schedule_attention_detail",
    ),
    # rutas de citas medicas
    path("quote_list/", QuoteListView.as_view(), name="quote_list"),
    path("quote_create/", QuoteCreateView.as_view(), name="quote_create"),
    path("quote_update/<int:pk>/", QuoteUpdateView.as_view(), name="quote_update"),
    path("quote_detail/<int:pk>/", QuoteDetailView.as_view(), name="quote_detail"),
    path("quote_delete/<int:pk>/", QuoteDeleteView.as_view(), name="quote_delete"),
    # rutas de servicios adicionales
    path(
        "servicio_list/", ServiciosAdicionalesListView.as_view(), name="servicio_list"
    ),
    path(
        "servicio_create/",
        ServiciosAdicionalesCreateView.as_view(),
        name="servicio_create",
    ),
    path(
        "servicio_update/<int:pk>/",
        ServiciosAdicionalesUpdateView.as_view(),
        name="servicio_update",
    ),
    path(
        "servicio_delete/<int:pk>/",
        ServiciosAdicionalesDeleteView.as_view(),
        name="servicio_delete",
    ),
    path(
        "servicio_detail/<int:pk>/",
        ServiciosAdicionalesDetailView.as_view(),
        name="servicio_detail",
    ),
    # rutas de certificados
    path("certificate_list/", CertificateListView.as_view(), name="certificate_list"),
    path(
        "certificate_create/",
        CertificateCreateView.as_view(),
        name="certificate_create",
    ),
    path(
        "certificate_update/<int:pk>/",
        CertificateUpdateView.as_view(),
        name="certificate_update",
    ),
    path(
        "certificate_delete/<int:pk>/",
        CertificateDeleteView.as_view(),
        name="certificate_delete",
    ),
    path(
        "certificate_detail/<int:pk>/",
        CertificateDetailView.as_view(),
        name="certificate_detail",
    ),
    path(
        "certificate_pdf/<int:pk>/",
        CertificatePDFView.as_view(),
        name="certificate_pdf",
    ),
    # rutas de fichas clinicas
    path(
        "clinical_record_list/",
        ClinicalRecordListView.as_view(),
        name="clinical_record_list",
    ),
    path(
        "clinical_record_detail/<int:pk>/",
        ClinicalRecordDetailView.as_view(),
        name="clinical_record_detail",
    ),
    path(
        "imprimir_historial_clinico/<int:pk>/",
        ImprimirHistorialClinico.as_view(),
        name="imprimir_historial_clinico",
    ),
    
    #Rutas examenes
    # path('examenes/', ExamenesListView.as_view(), name='examenes_list'),
    path('examenes_create/', ExaminationCreateView.as_view(), name='examenes_create'),
    # path('examenes_update/<int:pk>/', ExamenesUpdateView.as_view(), name='examenes_update'),
    # path('examenes_delete/<int:pk>/', ExamenesDeleteView.as_view(), name='examenes_delete'),
    #path('examenes_detail/<int:pk>/', ExamenesDetailView.as_view(), name='examenes_detail'),
    path("invoice_create/", InvoiceCreateView.as_view(), name="invoice_create"),
    path('factura/<int:pk>/', FacturaDetailView.as_view(), name='invoice_detail'),
    path('factura/payment/success/', payment_success, name='invoice_payment_success'),
    path('factura/payment/cancel/', payment_cancel, name='invoice_payment_cancel'),
    
    #rutas de examenes
    path('examination_list/', ExaminationListView.as_view(), name='examination_list'),
    path('examination_create/', ExaminationCreateView.as_view(), name='examination_create'),
    path('examination_update/<int:pk>/', ExaminationUpdateView.as_view(), name='examination_update'),
    path('examination_delete/<int:pk>/', ExaminationDeleteView.as_view(), name='examination_delete'),
    path('examination_detail/<int:pk>/', ExaminationDetailView.as_view(), name='examination_detail'),
]
