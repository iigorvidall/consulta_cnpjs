"""URLConf do projeto Django.

Encaminha a raiz para as rotas da app 'consulta' e expõe /admin/.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('consulta.urls')),
]
