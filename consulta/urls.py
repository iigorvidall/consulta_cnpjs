from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('export/resultado/csv/', views.export_resultado_csv, name='export_resultado_csv'),
    path('export/resultado/xlsx/', views.export_resultado_xlsx, name='export_resultado_xlsx'),
    path('export/historico/csv/', views.export_historico_csv, name='export_historico_csv'),
    path('export/historico/xlsx/', views.export_historico_xlsx, name='export_historico_xlsx'),
    path('status-retry/', views.status_retry, name='status_retry'),
    path('cnpj/<str:cnpj>/', views.ConsultaCNPJView.as_view(), name='consulta_cnpj'),
    # Streaming simples via polling
    path('jobs/start/', views.jobs_start, name='jobs_start'),
    path('jobs/step/', views.jobs_step, name='jobs_step'),
    path('jobs/finalize/', views.jobs_finalize, name='jobs_finalize'),
    path('jobs/pause/', views.jobs_pause, name='jobs_pause'),
    path('jobs/resume/', views.jobs_resume, name='jobs_resume'),
    path('jobs/cancel/', views.jobs_cancel, name='jobs_cancel'),
]
