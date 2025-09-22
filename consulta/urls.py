from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('export/resultado/csv/', views.export_resultado_csv, name='export_resultado_csv'),
    path('export/resultado/xlsx/', views.export_resultado_xlsx, name='export_resultado_xlsx'),
    path('export/historico/csv/', views.export_historico_csv, name='export_historico_csv'),
    path('export/historico/xlsx/', views.export_historico_xlsx, name='export_historico_xlsx'),
    path('status-retry/', views.status_retry, name='status_retry'),
]
