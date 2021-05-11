from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {
        'fields': ('username', 'password')
        }),
        ('Персональная информация', {
            'fields': ('last_name', 'first_name', 'patronymic', 'phone', 'email', 'position', 'photo')
            }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
            }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
            })
        )


admin.site.register(Order)
admin.site.register(WorkShift)
admin.site.register(Application)
admin.site.register(Partner)
admin.site.register(Entity)
admin.site.register(Person)
admin.site.register(Document)
admin.site.register(Raport)
admin.site.register(TransportationTo)
admin.site.register(TransportationOut)
admin.site.register(CustomUser, CustomUserAdmin)
