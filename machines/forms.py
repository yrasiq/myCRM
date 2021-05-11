from django import forms
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from .models import Machine


class MachineTypeForm(forms.Form):

    name = forms.CharField(label='Название', max_length=30)
    short_name = forms.CharField(label='Аббревиатура', max_length=5)
    prop_1 = forms.CharField(label='Хар-ка 1', max_length=30, required=False)
    prop_2 = forms.CharField(label='Хар-ка 2', max_length=30, required=False)
    prop_3 = forms.CharField(label='Хар-ка 3', max_length=30, required=False)
    options_1 = forms.CharField(label='Доп. оборудование 1', max_length=30, required=False)
    options_2 = forms.CharField(label='Доп. оборудование 2', max_length=30, required=False)
    options_3 = forms.CharField(label='Доп. оборудование 3', max_length=30, required=False)
    options_4 = forms.CharField(label='Доп. оборудование 4', max_length=30, required=False)
    options_5 = forms.CharField(label='Доп. оборудование 5', max_length=30, required=False)

    @staticmethod
    def options_constructor(machine_class: Machine.__subclasses__) -> Form:
        if machine_class not in Machine.__subclasses__():
            raise Exception(f'{machine_class.__name__} класс не является техникой')

        class OptionsFormWidgets(forms.Form):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                for field in self.fields:
                    self.fields[field].widget.attrs.update({'class': 'form-control'})

                    if field.endswith('_incoming'):
                        self.fields[field].widget.attrs.update({'placeholder': 'Покупка руб/ч'})
                    elif field.endswith('_outdoing'):
                        self.fields[field].widget.attrs.update({'placeholder': 'Продажа руб/ч'})

            def clean(self):
                options = self.cleaned_data
                if not options: return

                for key, value in options.items():
                    if key.endswith('_incoming'):
                        second_value = options.get(key.replace('_incoming', '_outdoing'))
                    elif key.endswith('_outdoing'):
                        second_value = options.get(key.replace('_outdoing', '_incoming'))

                    if type(value) == type(second_value): continue
                    raise ValidationError(f'Укажите оба поля стоимости')

                return super().clean()

        fields = {}
        [fields.update({
            f'{name}_incoming': forms.DecimalField(label=label, min_value=0, decimal_places=2, required=False),
            f'{name}_outdoing': forms.DecimalField(label='', min_value=0, decimal_places=2, required=False)
            }) for name, label in machine_class.get_options()]

        return type(machine_class.__name__ + 'OptionsForm', (OptionsFormWidgets,), fields)
