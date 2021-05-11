from .views import *
from django.urls import path
from django.contrib import admin


urlpatterns = [
    path('', admin.site.admin_view(CreateMachineType.as_view()), name='machine_type_create'),
    path('<str:type>/', admin.site.admin_view(UpdateMachineType.as_view()), name='machine_type_update'),
]
