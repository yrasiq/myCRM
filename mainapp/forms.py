from django import forms
from .models import Application, Order, Partner, TransportationOut, TransportationTo
from django.contrib.contenttypes.models import ContentType
from .utils import list_machine_type_contents


class NameModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.name


class TransportationForm(forms.ModelForm):

    def empty_fields(self) -> bool:
        if (
            not self.data['carrier']
            and not self.data['outdoing_cost']
            and not self.data['incoming_cost']
            and not self.data['incoming_pay_type']
            ):
            return True
        else:
            return False

    def is_valid(self) -> bool:
        if self.empty_fields(): return True
        return super().is_valid()

    def save(self, commit=True):
        if self.empty_fields():
            if self.instance.id:
                self.instance.delete()
            return
        self.instance.content_type_id = self.data['content_type_id']
        self.instance.object_id = self.data['object_id']
        return super().save(commit=commit)


class TransportationToForm(TransportationForm):

    class Meta:

        model = TransportationTo
        fields = ['carrier', 'incoming_pay_type', 'incoming_cost', 'outdoing_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['carrier'].widget.attrs.update({
            'id': 'id_carrier_transp_to',
        })
        self.fields['incoming_cost'].widget.attrs.update({
            'id': 'id_incoming_cost_transp_to',
        })
        self.fields['outdoing_cost'].widget.attrs.update({
            'id': 'id_outdoing_cost_transp_to',
        })
        self.fields['incoming_pay_type'].widget.attrs.update({
            'id': 'id_incoming_pay_type_transp_to',
        })


class TransportationOutForm(TransportationForm):

    class Meta:

        model = TransportationOut
        fields = ['carrier', 'incoming_pay_type', 'incoming_cost', 'outdoing_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['carrier'].widget.attrs.update({
            'id': 'id_carrier_transp_out',
        })
        self.fields['incoming_cost'].widget.attrs.update({
            'id': 'id_incoming_cost_transp_out',
        })
        self.fields['outdoing_cost'].widget.attrs.update({
            'id': 'id_outdoing_cost_transp_out',
        })
        self.fields['incoming_pay_type'].widget.attrs.update({
            'id': 'id_incoming_pay_type_transp_out',
        })


class ApplicationForm(forms.ModelForm):

    machine_type = NameModelChoiceField(
        widget=forms.Select(),
        label='Тип техники',
        queryset=ContentType.objects.filter(list_machine_type_contents())
    )

    class Meta:

        model = Application
        fields = [
            'manager',
            'machine_type',
            'start_date',
            'start_time',
            'duration',
            'adres',
            'contact',
            'customer',
            'outdoing_pay_type',
            'outdoing_cost',
            'supplier',
            'incoming_pay_type',
            'incoming_cost',
            'comment',
            ]
        widgets = {
            'comment': forms.Textarea(attrs={'rows': '2', 'cols': '10'}),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields['manager'].widget.attrs.update({
            'maxlength': '3',
        })
        self.fields['start_date'].widget.attrs.update({
            'maxlength': '10',
        })
        self.fields['start_time'].widget.attrs.update({
            'maxlength': '5',
        })
        self.fields['outdoing_cost'].widget.attrs.update({
            'min': '0',
            'placeholder': 'руб/час',
        })
        self.fields['incoming_cost'].widget.attrs.update({
            'min': '0',
            'placeholder': 'руб/час',
        })


class OrderForm(forms.ModelForm):

    machine_type = NameModelChoiceField(widget=forms.Select(), label='Тип техники',
    queryset=ContentType.objects.filter(list_machine_type_contents()))

    class Meta:

        model = Order
        fields = [
            'manager',
            'machine_type',
            'customer',
            'supplier',
            'adres',
            'contact',
            'outdoing_pay_type',
            'outdoing_cost',
            'incoming_pay_type',
            'incoming_cost',
            'start_date',
            'end_date'
            ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manager'].widget.attrs.update({
            'maxlength': '3',
        })
        self.fields['machine_type'].widget.attrs.update({
            'maxlength': '5',
        })
        self.fields['start_date'].widget.attrs.update({
            'maxlength': '10',
        })
        self.fields['end_date'].widget.attrs.update({
            'maxlength': '10',
        })
        self.fields['incoming_cost'].widget.attrs.update({
            'min': '0',
            'placeholder': 'руб/час',
        })
        self.fields['outdoing_cost'].widget.attrs.update({
            'min': '0',
            'placeholder': 'руб/час',
        })


class PartnerForm(forms.ModelForm):

    class Meta:

        model = Partner
        fields = ['name', 'manager', 'phone', 'email', 'adres', 'mail_adres']
