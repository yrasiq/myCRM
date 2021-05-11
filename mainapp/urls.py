from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('applications/', Applications.as_view(), name='applications'),
    path('applications/new/', CreateApplication.as_view(), name='applications_new'),
    path('applications/<int:pk>/', DetailApplication.as_view(), name='application'),
    path('applications/edit/<int:pk>/', UpdateApplication.as_view(), name='applications_edit'),
    path('orders/', Orders.as_view(), name='orders'),
    path('orders/<int:pk>/', DetailOrder.as_view(), name='order'),
    path('orders/edit/<int:pk>/', UpdateOrder.as_view(), name='orders_edit'),
    path('orders/workshift/<int:pk>/', UpdateWorkshifts.as_view(), name='order_workshifts'),
    path('machineworkshifts/', Workshifts.as_view(), name='machineworkshifts'),
    path('partners/', Partners.as_view(), name='partners'),
    path('partners/new/', CreatePartner.as_view(), name='partners_new'),
    path('partners/<int:pk>/', DetailPartner.as_view(), name='partner'),
    path('partners/edit/<int:pk>/', UpdatePartner.as_view(), name='partners_edit'),
    path('partners/<int:pk>/entity/', CreateEntity.as_view(), name='entity'),
    path('partners/entity/<int:pk>/', CreateEntity.as_view(), name='entity_edit'),
    path('machine/<str:type>/', MachineType.as_view(), name='machine_type'),
    path('machine/options/<int:machine_type_id>/', MachineOptionsForm.as_view(), name='machine_options'),
    path('machine/options/<int:machine_type_id>/<str:content_type>/<int:object_id>/', MachineOptionsForm.as_view(), name='machine_options'),
    path('machine/<str:type>/new/', CreateMachine.as_view(), name='machine_new'),
    path('machine/<str:type>/<int:pk>/', UpdateMachine.as_view(), name='machine_edit'),
    path('persons/', Persons.as_view(), name='persons'),
    path('persons/new/', CreatePerson.as_view(), name='person_new'),
    path('persons/<int:pk>/', UpdatePerson.as_view(), name='person_edit'),
    path('documents/', Documents.as_view(), name='documents'),
    path('documents/raport/', CreateRaport.as_view(), name='raport'),
    path('documents/raport/<int:pk>/', UpdateRaport.as_view(), name='raport_update'),
    path('documents/document/', CreateDocument.as_view(), name='document'),
    path('documents/document/<int:pk>/', UpdateDocument.as_view(), name='document_update'),
    path('employees/', Employees.as_view(), name='employees'),
    path('employees/<int:pk>/', DetailEmployee.as_view(), name='employee'),
    path('datetimeinfo/', views.datetimeinfo, name='datetimeinfo'),
    path('statistics/', views.home, name='statistics'),
    path('', views.home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
