from django.views.generic import FormView
from .forms import MachineTypeForm
from django.http.response import JsonResponse
from .models import CreateModel, UpdateModel
from .models import get_machine_types
from django.contrib.contenttypes.models import ContentType
from django.http.response import Http404
from django.db.models import PositiveIntegerField, BooleanField
from django.urls import reverse_lazy


class FormSetMachineType:

    form_class = MachineTypeForm
    template_name = 'admin/machinetype_form.html'

    def get_context_data(self, **kwargs):
        self.extra_context.update({'machine_types': [
            {'name': i, 'model': i.__name__.lower()}
            for i in get_machine_types()
            ]})
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        return JsonResponse({'form': form.as_table()}, status=400)

class CreateMachineType(FormSetMachineType, FormView):

    extra_context = {'title_form': 'Новый тип' , 'href': reverse_lazy('machine_type_create')}

    def form_valid(self, form):
        new_model = CreateModel(**form.cleaned_data)
        new_model.write_class()
        return JsonResponse({'message': 'Тип техники создан. Обновите страницу через несколько секунд.'})


class UpdateMachineType(FormSetMachineType, FormView):

    extra_context = {'title_form': 'Редактировать тип'}

    def form_valid(self, form):
        model = UpdateModel(self.model_name, **form.cleaned_data)
        model.update_class()
        return JsonResponse({'message': 'Изменения сохранены. Обновите страницу через несколько секунд.'})

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        del form.fields['name']
        return form

    def get_context_data(self, **kwargs):
        self.extra_context.update({'href': reverse_lazy('machine_type_update', kwargs=self.kwargs)})
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            model = ContentType.objects.get(model=self.kwargs.get('type')).model_class()
        except:
            raise Http404
        self.model_name = model.__name__
        if self.request.method == 'GET':
            fields = model.type_fields().copy()
            form_data = self.form_class.base_fields.copy()
            for key in form_data.keys():

                if key == 'short_name':
                    form_data[key] = model._meta.verbose_name
                else:
                    for k, v in fields.items():
                        if (isinstance(v, PositiveIntegerField) and key.startswith('prop') or
                            isinstance(v, BooleanField) and key.startswith('options')):
                            form_data[key] = v._verbose_name
                            del fields[k]
                            break
                    else:
                        form_data[key] = ''

            kwargs['data'] = form_data
        return kwargs
