from datetime import date, timedelta
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import redirect
from functools import reduce
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.conf import settings
import operator


class Cache:

    def __init__(self, session, cache_name, **kwargs):

        self.cache_name = cache_name
        self.type = kwargs.pop('request_type', [None])[0]
        if self.type not in ('filtrate', 'range'):
            kwargs = {i: j[0] for i, j in kwargs.items()}
        self.params = kwargs
        self.session = session

        self.set_stucture()
        if kwargs: self.write()

    def set_stucture(self):
        session = self.session
        cache_name = self.cache_name
        session.setdefault('cache', {})
        session['cache'].setdefault(cache_name, {})
        session['cache'][cache_name].setdefault('filters', {})
        session['cache'][cache_name].setdefault('ranges', {})
        session['cache'][cache_name].setdefault('sort', {})
        session['cache'][cache_name].setdefault('search', {})
        session['cache'][cache_name].setdefault('pagination', {})
        session['cache'][cache_name].setdefault('page', {})
        session.modified = True

    def write(self):

        type = self.type
        params = self.params
        session = self.session
        cache_name = self.cache_name

        if type == 'sort':
            session['cache'][cache_name]['sort'] = params

        elif type == 'filtrate':
            filt = list(*params.items())
            if 'clear' in filt[1]:
                session['cache'][cache_name]['filters'].pop(filt[0], None)
            else:
                session['cache'][cache_name]['filters'][filt[0]] = filt[1]

        elif type == 'range':
            filt = list(*params.items())
            if 'clear' in filt[1] or filt[1] == ['', '']:
                session['cache'][cache_name]['ranges'].pop(filt[0], None)
            else:
                session['cache'][cache_name]['ranges'][filt[0]] = filt[1]

        elif type == 'search':
            session['cache'][cache_name]['search'] = params

        elif type == 'pagination':
            session['cache'][cache_name]['page'] = params.get('page')

        session.modified = True


class SafePaginator(Paginator):
    def validate_number(self, number):
        try:
            return super(SafePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise


class ModelVarsMixin:

    def model_vars(self):
        var = vars(self).copy()
        var.pop('_state', None)
        return var


class DeleteError(ValidationError):

    pass


class OnlyAjaxResponseMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(getattr(self, 'success_url', 'home'))


class ChangeFieldsCleanMixin:

    def change_fields_clean(self, exclude=[]) -> dict:
        exclude += ['_state']
        old_obj = self.__class__.objects.get(id=self.id)
        old_data = old_obj.__dict__
        new_data = self.__dict__
        errors = {}
        changed_fields = {
            key: value for key, value in new_data.items()
            if key not in exclude
            and old_data[key] != value
            }
        for field in changed_fields:
            clean_field_method = getattr(self, 'clean_' + field, None)
            if clean_field_method:
                error = clean_field_method()
                if error: errors.update(error)

        return errors


class OptionsMixin:

    def options_info(self):
        options = self.options
        options_info = {}
        for key, value in options.items():

            if not value: continue

            option = key.replace('_incoming', '').replace('_outdoing', '')
            options_info.setdefault(option, {})

            if key.endswith('_incoming'):
                options_info[option]['incoming'] = value
            elif key.endswith('_outdoing'):
                options_info[option]['outdoing'] = value

            if options_info[option].get('verbose_name') is None:
                options_info[option]['verbose_name'] = self.machine_type.model_class()._meta.get_field(option).verbose_name

        return options_info


def file_size(value):
    limit = settings.MAX_FILE_SIZE * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Максимальный размер 10МБ')

def options_validate(options):
    if not options: return

    for key, value in options:
        if key.endswith('_incoming'):
            second_value = options.get(key.replace('_incoming', '_outdoing'))
        elif key.endswith('_outdoing'):
            second_value = options.get(key.replace('_outdoing', '_incoming'))

        if isinstance(type(value), type(second_value)): continue

        raise ValidationError(f'Укажите оба поля стоимости')

def list_machine_type_contents():
    from machines.models import get_machine_types #type: ignore
    return reduce(operator.or_, [Q(
        app_label=i._meta.app_label,
        model=i._meta.model_name) for i in get_machine_types()
    ])

def tomorow():
    return date.today() + timedelta(days=1)
