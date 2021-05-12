import operator
from django.core.checks import messages
from django.contrib.messages import get_messages
from django.db.models.deletion import ProtectedError
from django.utils.formats import localize
from django.db.models.query import QuerySet
from django.forms.forms import Form
from django.http.response import Http404, JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.edit import FormView
from .models import *
from functools import reduce
from .utils import Cache, DeleteError, SafePaginator, OnlyAjaxResponseMixin
from copy import deepcopy
from datetime import datetime
from .forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from machines.models import get_machine_types # type: ignore
from machines.forms import MachineTypeForm # type: ignore


class Workshifts(ListView):

    paginator_class = SafePaginator
    queryset = FullWorkShift.objects.all()
    template_name = 'mainapp/workshifts.html'
    context_object_name = 'output'
    paginate_by = 100
    titles = FullWorkShift.model_fields()
    cache_name = 'work_shifts'

    def get_context_data(self, **kwargs):

        context = super(Workshifts, self).get_context_data(**kwargs)
        context['output_title'] = self.titles
        context['cache'] = self.request.session.get('cache').get(self.cache_name)
        context['pagination_list'] = self.get_pagination_list()
        context['machine_types'] = get_machine_types()
        return context

    def get(self, request, *args, **kwargs):
        if request.is_ajax() and 'get_filter_list' in self.request.GET:
            return self.filter_list_response()
        else:
            self.check_messages(request)
            return super().get(self, request, *args, **kwargs)

    def check_messages(self, request):
        messages = get_messages(request)
        output_messages = {}
        for message in messages:
            try:
                id, type_ = message.message.split(': ')
                if type_ == 'was created successfully':
                    output_messages.setdefault(type_, [])
                    output_messages[type_].append(id)
            except:
                pass

        if output_messages.get('was created successfully'):
            self.queryset = self.queryset.annotate(changed=Case(
                When(id__in=output_messages['was created successfully'], then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField()
                ))

    def filter_list_response(self):
        self.calculate_queryset()
        filter_list = self.request.GET['get_filter_list']
        values_list = []

        for obj in self.queryset:
            value = getattr(obj, filter_list)
            if isinstance(value, ContentType):
                value = value.name
            elif filter_list == 'machine_type' and self.__class__ == Workshifts:
                value = ContentType.objects.get_for_id(value).name
            elif value is None:
                value = ''
            values_list.append(str(localize(value)))

        values_list = sorted(list(set(values_list)))
        return JsonResponse(values_list, safe=False)

    def setup(self, request, *args, **kwargs):
        self.get_validator(request.GET.copy())
        self.session = request.session
        Cache(self.session, self.cache_name, **request.GET.copy())
        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        self.calculate_queryset()
        return super().get_queryset()

    def calculate_queryset(self):

        queryset = self.queryset
        titles = self.titles
        filters = self.session['cache'][self.cache_name]['filters']
        sort = self.session['cache'][self.cache_name]['sort']
        search = self.session['cache'][self.cache_name]['search']
        ranges = deepcopy(self.session['cache'][self.cache_name]['ranges'])

        if ranges:
            for key in ranges.copy():
                try:
                    for i, j in enumerate(ranges[key]):
                        if j:
                            ranges[key][i] = datetime.strptime(j, '%d.%m.%Y').date()
                except:
                    pass

            for key, value in ranges.items():
                if value[0]:
                    queryset = queryset.filter(**{"%s__gte" % (key): value[0]})
                if value[1]:
                    queryset = queryset.filter(**{"%s__lte" % (key): value[1]})

        if filters:
            filters_copy = filters.copy()
            for i in filters:

                if i == 'machine_type':
                    if self.queryset.model == FullWorkShift:
                        i_filter = 'order__' + i
                    else:
                        i_filter = i

                    filters_copy["%s__model__in" % (i_filter)] = [
                        j.__name__.lower()
                        for j in get_machine_types()
                        if j._meta.verbose_name in filters_copy[i]
                        ]
                    del filters_copy[i]

                elif self.queryset.model != FullWorkShift and i in ('customer', 'supplier', 'partner'):
                    filters_copy["%s__name__in" % (i)] = filters_copy.pop(i)

                elif i in ('incoming_act', 'incoming_invoice', 'outdoing_act', 'outdoing_invoice'):
                    filters_copy["%s__number__in" % (i)] = filters_copy.pop(i)

                elif i == 'full_name':
                    full_name = filters_copy.pop(i)[0].split(' ')
                    filters_copy["last_name"] = full_name[0]
                    try:
                        filters_copy["first_name"] = full_name[1]
                    except IndexError:
                        filters_copy["first_name"] = ''
                    try:
                        filters_copy["patronymic"] = full_name[2]
                    except IndexError:
                        filters_copy["patronymic"] = ''
                else:
                    filters_copy["%s__in" % (i)] = filters_copy.pop(i)

            queryset = queryset.filter(**filters_copy)

        if search:
            search_set = []
            for i in self.queryset.model.search_fields():

                if i == 'machine_type':
                    if self.queryset.model == FullWorkShift:
                        i_filter = 'order__' + i
                    else:
                        i_filter = i

                    search_set.append(Q(**{"%s__model__in" % (i_filter): [
                        name.__name__.lower() for name in get_machine_types()
                        if search['search'].lower() in name._meta.verbose_name.lower()
                        ]}))

                elif self.queryset.model != FullWorkShift and i in ('customer', 'supplier', 'partner'):
                    search_set.append(Q(**{"%s__name__icontains" % (i): search['search']}))

                elif i in ('incoming_act', 'incoming_invoice', 'outdoing_act', 'outdoing_invoice'):
                    search_set.append(Q(**{"%s__number__icontains" % (i): search['search']}))

                elif i == 'manager' and self.queryset.model != FullWorkShift:
                    search_set.append(Q(**{"%s__username__icontains" % (i): search['search']}))

                elif i == 'raport':
                    search_set.append(Q(**{"%s__id__icontains" % (i): search['search']}))

                elif i == 'full_name':
                    search_request = search['search'].split(' ')
                    full_name_query = reduce(operator.or_ ,(Q(
                        Q(last_name__icontains=i) |
                        Q(first_name__icontains=i) |
                        Q(patronymic__icontains=i)
                        ) for i in search_request))
                    search_set.append(full_name_query)
                else:
                    search_set.append(Q(**{"%s__icontains" % (i): search['search']}))

            search_set = reduce(operator.or_,(search_set))
            queryset = queryset.filter(search_set)

        if sort:
            sort = list(sort.copy().popitem())
            for i in titles:
                if titles[i] == sort[0]:
                    sort[0] = i
                    break

            if sort[0] in ('machine_type', 'full_name'):

                if sort[1] == "sort_down":
                    rev = False
                elif sort[1] == "sort_up":
                    rev = True

                if sort[0] == 'machine_type':

                    if self.queryset.model == FullWorkShift:
                        queryset = sorted(queryset, key=lambda name: name.order.machine_type.name, reverse=rev)
                    else:
                        queryset = sorted(queryset, key=lambda name: name.machine_type.name, reverse=rev)

                elif sort[0] == 'full_name':
                    queryset = sorted(queryset, key=lambda name: name.full_name(), reverse=rev)

            else:
                if self.queryset.model != FullWorkShift and sort[0] in ('customer', 'supplier', 'partner'):
                    sort[0] += '__name'
                elif sort[0] in ('incoming_act', 'incoming_invoice', 'outdoing_act', 'outdoing_invoice'):
                    sort[0] += '__number'

                if sort[1] == "sort_down":
                    sort = sort[0]
                elif sort[1] == "sort_up":
                    sort = '-' + sort[0]

                queryset = queryset.order_by(sort)

        self.kwargs[self.page_kwarg] = self.session['cache'][self.cache_name]['page']
        self.queryset = queryset


    def get_pagination_list(self, **kwargs):

        page_obj = super(Workshifts, self).get_context_data(**kwargs)['page_obj']
        pagination = {}

        if page_obj.has_other_pages():

            if page_obj.has_previous():
                pagination['«'] = 1

            if page_obj.has_previous():
                pagination['‹'] = page_obj.previous_page_number()

            for num_page in page_obj.paginator.page_range:

                if page_obj.number == num_page:
                    pagination['active'] = num_page

                elif num_page >= page_obj.number - 2 and num_page <= page_obj.number + 2:
                    pagination[str(num_page)] = num_page

            if page_obj.has_next():
                pagination['›'] = page_obj.next_page_number()

            if page_obj.has_next():
                pagination['»'] = page_obj.paginator.num_pages

        return [[i, j] for i, j in pagination.items()]

    def get_validator(self, get):

        if len(get) > 0:
            try:

                if len(get) == 1:

                    if 'get_filter_list' not in get or get['get_filter_list'] not in self.titles:
                        Exception
                    else:
                        return

                elif len(get) == 2:

                    request_type = get.pop('request_type', None)
                    field, value = get.popitem()

                    if len(request_type) > 1:
                        raise Exception
                    else:
                        request_type = request_type[0]
                    if not request_type:
                        raise Exception
                    if request_type not in ('filtrate', 'range'):
                        value = value[0]

                    if request_type in ('filtrate', 'sort'):
                        if field not in self.titles:
                            raise Exception
                        elif 'sort' in request_type and value not in ('sort_down', 'sort_up'):
                            raise Exception
                    elif request_type == 'search':
                        if field != 'search':
                            raise Exception
                    elif request_type == 'pagination':
                        int(value)
                    elif request_type == 'range':
                        if field in self.titles:
                            if len(value) <= 2:
                                if field == 'date':
                                    [datetime.strptime(i, '%d.%m.%Y') for i in value if i]
                            else:
                                raise Exception
                        else:
                            raise Exception
                    else:
                        raise Exception

            except:
                raise Exception('invalid parametrs in GET request')


class Documents(ListView):

    queryset = WorkShift.objects.all()
    queryset_transp_to = TransportationTo.objects.filter(
        content_type=ContentType.objects.get_for_model(Order),
        )
    queryset_transp_out = TransportationOut.objects.filter(
        content_type=ContentType.objects.get_for_model(Order),
        )
    template_name = 'mainapp/documents.html'
    context_object_name = 'output'
    paginator_class = SafePaginator
    paginate_by = 100
    extra_context = {}

    def get_context_data(self, **kwargs):
        self.extra_context.update({'machine_types': get_machine_types()})
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        get = self.request.GET.copy()
        doc = get.pop('document', None)
        doc_format, doc_type = self.parse_doctype(get)
        filters = {
            'filter': [],
            'filter_transp_to': [],
            'filter_transp_out': []
            }

        if doc == ['raport']:
            filters = self.raport_query(
                get=get, **filters
                )
        elif doc == ['document']:
            filters = self.doctype_query(
                doc_format=doc_format, doc_type=doc_type, **filters
                )
            entity = get.get('entity')
            filters = self.entity_query(
                entity=entity, doc_format=doc_format, **filters
                )
            date = get.get('date')
            filters = self.date_query(
                date=date, **filters
                )
        all_queryset = sorted((
            list(self.queryset.filter(*filters['filter']))
            + list(self.queryset_transp_to.filter(*filters['filter_transp_to']))
            + list(self.queryset_transp_out.filter(*filters['filter_transp_out']))
            ), reverse=True, key=self.sort_queryset)

        if doc_format and doc_type and doc == ['document']:
            doctype = f'{doc_format}_{doc_type}'
        elif doc == ['raport']:
            doctype = 'raport'
        else:
            doctype = None

        self.extra_context = {'doc': self.get_extra(doctype, *all_queryset)}
        self.queryset = all_queryset
        return super().get_queryset()

    @staticmethod
    def date_query(filter: list, filter_transp_to: list,
    filter_transp_out: list, date: str) -> tuple:

        if not date:
            return {
                'filter': filter,
                'filter_transp_to': filter_transp_to,
                'filter_transp_out': filter_transp_out
                }

        date = datetime.strptime(date, '%d.%m.%Y')
        filter.append(Q(date__lte=date))
        filter_transp_to.append(Q(order__start_date__lte=date))
        filter_transp_out.append(Q(order__end_date__lte=date))

        return {
            'filter': filter,
            'filter_transp_to': filter_transp_to,
            'filter_transp_out': filter_transp_out
            }

    @staticmethod
    def entity_query(filter: list, filter_transp_to: list,
    filter_transp_out: list, entity: str, doc_format: str) -> tuple:

        if not entity:
            return {
                'filter': filter,
                'filter_transp_to': filter_transp_to,
                'filter_transp_out': filter_transp_out
                }
        outdoing = Q(order__customer__entity=entity)
        incoming = Q(order__supplier__entity=entity)
        if doc_format == 'outdoing':
            filter.append(outdoing)
            filter_transp_to.append(outdoing)
            filter_transp_out.append(outdoing)
        elif doc_format == 'incoming':
            filter.append(incoming)
            filter_transp_to.append(incoming)
            filter_transp_out.append(incoming)
        else:
            filter.append(incoming | outdoing)

        return {
            'filter': filter,
            'filter_transp_to': filter_transp_to,
            'filter_transp_out': filter_transp_out
            }

    @staticmethod
    def doctype_query(filter: list, filter_transp_to: list,
    filter_transp_out: list, doc_format: str, doc_type: str) -> tuple:

        if doc_format:
            if doc_type == 'invoice':
                filter_query = Q(
                    **{f'order__{doc_format}_pay_type': 'НДС'}
                    )
                transp_query = Q(object_id__in=Order.objects.filter(
                    **{f'{doc_format}_pay_type': 'НДС'}
                    )) if doc_format == 'outdoing' else Q(
                        incoming_pay_type='НДС'
                        )
                filter.append(filter_query)
                filter_transp_to.append(transp_query)
                filter_transp_out.append(transp_query)
            else:
                filter_query = Q(
                    **{f'order__{doc_format}_pay_type__in': ['БНДС', 'НДС']}
                    )
                transp_query = Q(object_id__in=Order.objects.filter(
                    **{f'{doc_format}_pay_type__in': ['БНДС', 'НДС']}
                    )) if doc_format == 'outdoing' else Q(
                        incoming_pay_type__in=['БНДС', 'НДС']
                        )
                filter.append(filter_query)
                filter_transp_to.append(transp_query)
                filter_transp_out.append(transp_query)
        else:
            if doc_type == 'invoice':
                filter_query = Q(
                    Q(order__incoming_pay_type='НДС')
                    | Q(order__outdoing_pay_type='НДС')
                    )
                transp_query = Q(
                    Q(incoming_pay_type='НДС') |
                    Q(object_id__in=Order.objects.filter(outdoing_pay_type='НДС'))
                    )
                filter.append(filter_query)
                filter_transp_to.append(transp_query)
                filter_transp_out.append(transp_query)
            else:
                transp_query = Q(
                    Q(incoming_pay_type__in=['БНДС', 'НДС']) |
                    Q(object_id__in=Order.objects.filter(outdoing_pay_type__in=['БНДС', 'НДС']))
                    )
                filter_query = Q(
                    Q(order__incoming_pay_type__in=['БНДС', 'НДС'])
                    | Q(order__outdoing_pay_type__in=['БНДС', 'НДС'])
                    )
                filter.append(filter_query)
                filter_transp_to.append(transp_query)
                filter_transp_out.append(transp_query)

        return {
            'filter': filter,
            'filter_transp_to': filter_transp_to,
            'filter_transp_out': filter_transp_out
            }

    @staticmethod
    def raport_query(filter: list, filter_transp_to: list,
    filter_transp_out: list, get: dict) -> tuple:

        if get.get('start_date'):
            start_date = datetime.strptime(get['start_date'], '%d.%m.%Y')
            filter.append(Q(date__gte=start_date))
            filter_transp_to.append(Q(order__start_date__gte=start_date))
            filter_transp_out.append(Q(order__end_date__gte=start_date))

        if get.get('end_date'):
            end_date = datetime.strptime(get['end_date'], '%d.%m.%Y')
            filter.append(Q(date__lte=end_date))
            filter_transp_to.append(Q(order__start_date__lte=end_date))
            filter_transp_out.append(Q(order__end_date__lte=end_date))

        if get.get('order'):
            filter.append(Q(order=get['order']))
            filter_transp_to.append(Q(order=get['order']))
            filter_transp_out.append(Q(order=get['order']))

        return {
            'filter': filter,
            'filter_transp_to': filter_transp_to,
            'filter_transp_out': filter_transp_out
            }

    @staticmethod
    def sort_queryset(obj):
        if isinstance(obj, TransportationOut):
            return obj.content_object.end_date + timedelta(days=1)
        elif isinstance(obj, TransportationTo):
            return obj.content_object.start_date
        elif isinstance(obj, WorkShift):
            return obj.date
        else:
            raise Exception('Неизвестный объект для сортировки')

    @staticmethod
    def parse_doctype(get: dict) -> tuple:

        if get.get('type') == 'АТ':
            doc_type = 'act'
        elif get.get('type') == 'СФ':
            doc_type = 'invoice'
        else:
            doc_type = None

        if get.get('format') == 'ИХ':
            doc_format = 'outdoing'
        elif get.get('format') == 'ВХ':
            doc_format = 'incoming'
        else:
            doc_format = None

        return (doc_format, doc_type)

    @staticmethod
    def get_extra(document: str, *queryset: list) -> list:

        if document is None:
            extra = []
        elif document == 'raport':
            extra = sorted(list(set([
                (getattr(i, document).pk, getattr(i, document))
                for i in queryset if getattr(i, document)
                ])), reverse=True)

        elif document in (
            'incoming_act', 'incoming_invoice',
            'outdoing_act', 'outdoing_invoice',
            ):
            extra = sorted(list(set([
                (getattr(i, document).pk, getattr(i, document).number)
                for i in queryset if getattr(i, document)
                ])), reverse=True)

        else:
            raise Exception('Неизвестный тип документа')

        return extra


class Persons(Workshifts):

    queryset = Person.objects.all()
    template_name = 'mainapp/persons.html'
    titles = Person.model_fields()
    cache_name = 'persons'


class MachineType(Workshifts):

    template_name = 'mainapp/machines.html'

    def get_context_data(self, **kwargs):
        self.extra_context.update({'actions': {
            'actions': {
                '1': [
                    reverse('partner', kwargs={'pk': i})
                    for i in self.queryset.values_list('partner__id', flat=True)
                    ]
                }
            }})
        return super().get_context_data(**kwargs)

    def setup(self, request, *args, **kwargs):
        for i in get_machine_types():
            if i.name() == kwargs['type']:
                self.queryset = i.objects.all()
                self.titles = i.model_fields()
                self.cache_name = i.name() + 'dynamic'
                self.extra_context = {'title': i._meta.verbose_name}
                break
        else:
            raise Http404

        return super().setup(request, *args, **kwargs)


class Partners(Workshifts):

    queryset = Partner.objects.all()
    template_name = 'mainapp/partners.html'
    titles = Partner.model_fields()
    cache_name = 'partners'


class Employees(Workshifts):

    queryset = CustomUser.objects.all()
    template_name = 'mainapp/employees.html'
    titles = CustomUser.model_fields()
    cache_name = 'employees'

    def filter_list_response(self):
        if self.request.GET['get_filter_list'] == 'full_name':
            self.calculate_queryset()
            values_list = sorted(list(set([i.full_name() for i in self.queryset])))
            return JsonResponse(values_list, safe=False)
        else:
            return super().filter_list_response()


class Orders(Workshifts):

    queryset = Order.objects.all()
    template_name = 'mainapp/orders.html'
    titles = Order.model_fields()
    cache_name = 'orders'


class Applications(Workshifts):

    queryset = Application.objects.all()
    template_name = 'mainapp/applications.html'
    titles = Application.model_fields()
    cache_name = 'applications'


class DetailEmployee(DetailView):

    model = CustomUser
    template_name = 'mainapp/employee.html'
    context_object_name = 'output'

    def get(self, request, *args, **kwargs):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        obj = self.get_object()

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%d.%m.%Y').date()
            except:
                response = super().get(request, *args, **kwargs)
                response.status_code = 400
                return response

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%d.%m.%Y').date()
            except:
                response = super().get(request, *args, **kwargs)
                response.status_code = 400
                return response

        if obj.position == 'МЕН':
            self.extra_context = Statistics(
                Q(order__manager=obj),
                start_date,
                end_date,
                ).full()

        return super().get(request, *args, **kwargs)


class DetailApplication(DetailView):

    model = Application
    template_name = 'mainapp/application.html'
    context_object_name = 'output'


class DetailPartner(DetailView):

    model = Partner
    template_name = 'mainapp/partner.html'
    context_object_name = 'output'


class DetailOrder(DetailView):

    model = Order
    template_name = 'mainapp/order.html'
    context_object_name = 'output'

    def get_context_data(self, **kwargs):
        self.extra_context = {
            'statistic': Statistics(
                Q(order=self.object),
                self.object.start_date,
                self.object.end_date
                ).__dict__
            }
        return super().get_context_data(**kwargs)


class FormSet(OnlyAjaxResponseMixin, SuccessMessageMixin):

    success_message = "%(id)s: was created successfully"
    template_name = 'form.html'
    context_object_name = 'output'

    def get_success_message(self, cleaned_data=None):
        if self.object.id:
            return self.success_message % {'id': self.object.id}

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response


class UpdateMachine(FormSet, UpdateView):

    template_name = 'mainapp/machine_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.POST.get('type', None) == 'delete':
            self.get_object().delete()
            return redirect(self.success_url)
        else:
            return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        for i in get_machine_types():
            if i.name() == kwargs['type']:
                self.model = i
                self.fields = i.model_fields()
                self.success_url = reverse('machine_type', kwargs={'type': kwargs['type']})
                self.extra_context = {
                    'id': 'update_machine_form',
                    'href': reverse('machine_edit', kwargs=kwargs)
                    }
                break
        else:
            raise Http404
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'header': self.object._meta.verbose_name + ' ' + str(self.object.pk),
            })
        return super().get_context_data(**kwargs)


class FormRaportSet(FormSet):

    success_url = '/documents/'
    template_name = 'mainapp/document_form.html'

    def form_valid(self, form):
        return self.check(form)

    def check(self, form: Form) -> None:
        workshifts = self.request.POST.get('workshift')
        transportation_to = self.request.POST.get('transportation_to')
        transportation_out = self.request.POST.get('transportation_out')
        error = self.check_empty(workshifts + transportation_to + transportation_out)
        if error is None:

            workshifts = [int(i) for i in workshifts.split(',') if i]
            transportation_to = [int(i) for i in transportation_to.split(',') if i]
            transportation_out = [int(i) for i in transportation_out.split(',') if i]
            workshifts = WorkShift.objects.filter(pk__in=workshifts)
            transportation_to = TransportationTo.objects.filter(pk__in=transportation_to)
            transportation_out = TransportationOut.objects.filter(pk__in=transportation_out)
            for i in (
                self.check_hours_sum(workshifts, form),
                self.check_daterange(workshifts, form),
                self.check_daterange(transportation_to, form),
                self.check_daterange(transportation_out, form),
                self.check_contains(workshifts, form),
                self.check_contains(transportation_to, form),
                self.check_contains(transportation_out, form),
                ):
                if i is not None:
                    error = i
                    break
            else:
                return self.check_success(workshifts, transportation_to, transportation_out, form)

        form.add_error(field=None, error=error)
        return self.render_to_response(self.get_context_data(form=form), status=400)

    def check_success(
        self, workshifts: QuerySet, transportation_to: QuerySet, transportation_out: QuerySet, form: Form
        ) -> JsonResponse:

        obj = form.save()
        workshifts.update(raport=obj)
        transportation_to.update(raport=obj)
        transportation_out.update(raport=obj)
        return JsonResponse({
            'workshifts': list(workshifts.values_list('id', flat=True)),
            'transportation_to': list(transportation_to.values_list('id', flat=True)),
            'transportation_out': list(transportation_out.values_list('id', flat=True)),
            'object': form.instance.pk,
            }, safe=False)

    @staticmethod
    def check_empty(workshifts):
        if not workshifts:
            return ValidationError('Добавте смены в рапорт')

    @staticmethod
    def check_hours_sum(workshifts: QuerySet, form: Form) -> None or ValidationError:
        if not workshifts.exists(): return
        if form.instance.hours_sum != workshifts.aggregate(sum_hours=Sum('hours'))['sum_hours']:
            return ValidationError('Часы в рапорте и сменах не равны')

    @staticmethod
    def check_daterange(workshifts: QuerySet, form: Form) -> None or ValidationError:

        if not workshifts.exists():
            return
        elif isinstance(workshifts.first(), TransportationTo):
            field = 'order__start_date'
        elif isinstance(workshifts.first(), TransportationOut):
            field = 'order__end_date'
        elif isinstance(workshifts.first(), WorkShift):
            field = 'date'
        else:
            raise Exception('Недопустимый класс модели')

        if any([
            True for i in workshifts.values_list(field, flat=True)
            if i < datetime.strptime(form.data['start_date'], '%d.%m.%Y').date()
            or i > datetime.strptime(form.data['end_date'], '%d.%m.%Y').date()
            ]):
            return ValidationError('Смены не в диапазоне дат рапорта')

    @staticmethod
    def check_contains(workshifts: QuerySet, form: Form) -> None or ValidationError:
        if workshifts.exclude(raport=None).exists():
            return ValidationError('Смена содержит рапорт')


class CreateRaport(FormRaportSet, CreateView):

    model = Raport
    fields = model.model_fields()


class UpdateRaport(FormRaportSet, UpdateView):

    model = Raport
    fields = model.model_fields()

    def post(self, request, *args, **kwargs):
        if request.POST.get('command') == 'delete':
            self.get_object().delete()
            return JsonResponse({})
        else:
            return super().post(request, *args, **kwargs)

    def check_success(self, workshifts: QuerySet, transportation_to: QuerySet,
    transportation_out: QuerySet, form: Form) -> JsonResponse:

        WorkShift.objects.filter(raport=form.instance).update(raport=None)
        TransportationTo.objects.filter(raport=form.instance).update(raport=None)
        TransportationOut.objects.filter(raport=form.instance).update(raport=None)
        return super().check_success(workshifts, transportation_to, transportation_out, form)

    @staticmethod
    def check_contains(workshifts: QuerySet, form: Form) -> None or ValidationError:
        if workshifts.exclude(Q(raport=None) | Q(raport__pk=form.instance.pk)).exists():
            return ValidationError('Смена содержит рапорт')


class FormDocumentSet(FormSet):

    success_url = '/documents/'
    template_name = 'mainapp/document_form.html'

    def form_valid(self, form: Form):
        return self.check(form)

    def check(self, form: Form) -> None:
        workshifts = self.request.POST.get('workshift')
        transportation_to = self.request.POST.get('transportation_to')
        transportation_out = self.request.POST.get('transportation_out')
        error = self.check_empty(workshifts + transportation_to + transportation_out)
        if error is None:

            workshifts = [int(i) for i in workshifts.split(',') if i]
            transportation_to = [int(i) for i in transportation_to.split(',') if i]
            transportation_out = [int(i) for i in transportation_out.split(',') if i]
            workshifts = WorkShift.objects.filter(pk__in=workshifts)
            transportation_to = TransportationTo.objects.filter(pk__in=transportation_to)
            transportation_out = TransportationOut.objects.filter(pk__in=transportation_out)
            for i in (
                self.check_sum(workshifts, transportation_to, transportation_out, form),
                self.check_date(workshifts, form),
                self.check_date(transportation_to, form),
                self.check_date(transportation_out, form),
                self.check_contains(workshifts, form),
                self.check_contains(transportation_to, form),
                self.check_contains(transportation_out, form),
                self.check_pay_type(workshifts, form),
                self.check_pay_type(transportation_to, form),
                self.check_pay_type(transportation_out, form),
                ):
                if i is not None:
                    error = i
                    break
            else:
                return self.check_success(workshifts, transportation_to, transportation_out, form)

        form.add_error(field=None, error=error)
        return self.render_to_response(self.get_context_data(form=form), status=400)

    @staticmethod
    def check_empty(workshifts) -> None or ValidationError:
        if not workshifts:
            return ValidationError('Добавте смены в документ')

    @staticmethod
    def check_sum(workshifts: QuerySet, transportation_to: QuerySet,
    transportation_out: QuerySet, form: Form) -> None or ValidationError:

        if form.data['format'] == 'ВХ':
            cost = 'incoming_cost'
        elif form.data['format'] == 'ИХ':
            cost = 'outdoing_cost'
        else:
            return ValidationError('Недопустимый формат документа')

        transp_to_sum = transportation_to.aggregate(sum=Sum(cost))['sum'] or 0
        transp_out_sum = transportation_out.aggregate(sum=Sum(cost))['sum'] or 0
        workshifts_sum = Decimal(0.00)
        for i in workshifts:
            option_cost = Decimal(0.00)
            if i.options:
                for val in i.order.options_info().values():
                    if val.get('verbose_name') == i.options:
                        option_cost = Decimal(val.get(cost.replace('_cost', '')))
                        break
            workshifts_sum += i.hours * (getattr(i.order, cost) + option_cost)
        workshifts_sum = round(workshifts_sum, 2)

        if form.instance.summ != transp_to_sum + transp_out_sum + workshifts_sum:
            return ValidationError('Суммы документа и смен не равны')

    @staticmethod
    def check_pay_type(workshifts: QuerySet, form: Form) -> None or ValidationError:
        if not workshifts.exists(): return
        format_doc = 'incoming' if form.instance.format == 'ВХ' else 'outdoing'

        if workshifts.model == WorkShift:
            if (
                form.instance.type == 'АТ' and
                workshifts.filter(**{f'order__{format_doc}_pay_type': 'НАЛ'}).exists()
                ): return ValidationError('Акт не относится к наличным сменам')
            elif (
                form.instance.type == 'СФ' and
                workshifts.exclude(**{f'order__{format_doc}_pay_type': 'НДС'}).exists()
                ): return ValidationError('Счет-фактура только для смен с НДС')

        elif workshifts.model in Transportation.__subclasses__():

            if form.instance.type == 'АТ':
                if (
                    format_doc == 'incoming' and
                    workshifts.filter(incoming_pay_type='НАЛ').exists()
                    ): return ValidationError('Акт не относится к наличным перевозкам')
                elif (
                    format_doc == 'outdoing' and
                    workshifts.filter(object_id__in=Order.objects.filter(outdoing_pay_type='НАЛ')).exists()
                    ): return ValidationError('Акт не относится к наличным перевозкам')

            elif form.instance.type == 'СФ':
                if (
                    format_doc == 'incoming' and
                    workshifts.exclude(incoming_pay_type='НДС').exists()
                    ): return ValidationError('Счет-фактура только для перевозок с НДС')
                elif (
                    format_doc == 'outdoing' and
                    workshifts.filter(object_id__in=Order.objects.exclude(outdoing_pay_type='НДС')).exists()
                    ): return ValidationError('Счет-фактура только для перевозок с НДС')

            if format_doc == 'incoming' and workshifts.filter(incoming_cost=None).exists():
                return ValidationError('Не назначен перевозчик')

        else:
            raise Exception(f'{workshifts.model} invalid model')

    @staticmethod
    def check_date(workshifts: QuerySet, form: Form) -> None or ValidationError:

        if not workshifts.exists():
            return
        elif isinstance(workshifts.first(), TransportationTo):
            field = 'order__start_date'
        elif isinstance(workshifts.first(), TransportationOut):
            field = 'order__end_date'
        elif isinstance(workshifts.first(), WorkShift):
            field = 'date'
        else:
            raise Exception('Недопустимый класс модели')

        if any([
            True for i in workshifts.values_list(field, flat=True)
            if i > datetime.strptime(form.data['date'], '%d.%m.%Y').date()
            ]):
            return ValidationError('Смена позже даты документа')

    def check_contains(self, workshifts: QuerySet, form: Form) -> None or ValidationError:
        fieldname = self.get_ws_doc_fieldname(form)
        if workshifts.exclude(**{fieldname: None}).exists():
            return ValidationError('Смена содержит рапорт')

    def check_success(self, workshifts: QuerySet, transportation_to: QuerySet,
    transportation_out: QuerySet, form: Form) -> JsonResponse:

        fieldname = self.get_ws_doc_fieldname(form)
        obj = form.save()
        workshifts.update(**{fieldname: obj})
        transportation_to.update(**{fieldname: obj})
        transportation_out.update(**{fieldname: obj})
        return JsonResponse({
            'workshifts': list(workshifts.values_list('id', flat=True)),
            'transportation_to': list(transportation_to.values_list('id', flat=True)),
            'transportation_out': list(transportation_out.values_list('id', flat=True)),
            'object': form.instance.pk,
            }, safe=False)

    @staticmethod
    def get_ws_doc_fieldname(form: Form) -> str:
        format = 'incoming' if form.data['format'] == 'ВХ' else 'outdoing'
        type = 'act' if form.data['type'] == 'АТ' else 'invoice'
        return f'{format}_{type}'


class CreateDocument(FormDocumentSet, CreateView):

    model = Document
    fields = model.model_fields()


class UpdateDocument(FormDocumentSet, UpdateView):

    model = Document
    fields = model.model_fields()

    def post(self, request, *args, **kwargs):
        if request.POST.get('command') == 'delete':
            self.get_object().delete()
            return JsonResponse({})
        else:
            return super().post(request, *args, **kwargs)

    def check_success(self, workshifts: QuerySet, transportation_to: QuerySet, transportation_out: QuerySet, form: Form) -> JsonResponse:
        fieldname = self.get_ws_doc_fieldname(form)
        WorkShift.objects.filter(**{fieldname: form.instance}).update(**{fieldname: None})
        TransportationTo.objects.filter(**{fieldname: form.instance}).update(**{fieldname: None})
        TransportationOut.objects.filter(**{fieldname: form.instance}).update(**{fieldname: None})
        return super().check_success(workshifts, transportation_to, transportation_out, form)

    def check_contains(self, workshifts: QuerySet, form: Form) -> None or ValidationError:
        fieldname = self.get_ws_doc_fieldname(form)
        if workshifts.exclude(Q(**{fieldname: None}) | Q(**{fieldname + '__pk': form.instance.pk})).exists():
            return ValidationError('Смена содержит документ этого типа')


class CreatePerson(FormSet, CreateView):

    model = Person
    fields = Person.model_fields()
    success_url = '/persons/'
    extra_context = {
        'id': 'create_person_form',
        'href': reverse_lazy('person_new'),
        'header': 'Новый контакт',
        }


class UpdatePerson(FormSet, UpdateView):

    model = Person
    fields = Person.model_fields()
    success_url = '/persons/'
    extra_context = {'id': 'update_person_form'}

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'href': reverse('person_edit', kwargs=self.kwargs),
            'header': self.get_object().name,
        })
        return super().get_context_data(**kwargs)

class UpdatePartner(FormSet, UpdateView):

    model = Partner
    form_class = PartnerForm
    success_url = '/partners/'
    extra_context = {'id': 'update_partner_form'}

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'header': self.get_object().name,
            'href': self.request.get_full_path(),
            })
        return super().get_context_data(**kwargs)


class MultiFormMixin(FormSet):

    transp_to_form = TransportationToForm
    transp_out_form = TransportationOutForm
    machine_options_form = None

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if self.request.method in ('POST', 'PUT'):

            options = self.serrialize_request_key('machine_options_form')
            form.instance.options = options

        return form

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'transp_to_form': kwargs.get('transp_to_form') or self.transp_to_form(
                instance=self.object.transportation_to.first()
                ),
            'transp_out_form': kwargs.get('transp_out_form') or self.transp_out_form(
                instance=self.object.transportation_out.first()
                ),
            'machine_options_form': kwargs.get('machine_options_form') or self.machine_options_form,
            })
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        machine_options_form = self.get_machine_options_form(request)
        transp_to_form = self.get_another_form(self.object.transportation_to.first(), 'transp_to_form')
        transp_out_form = self.get_another_form(self.object.transportation_out.first(), 'transp_out_form')

        if (
            transp_out_form.is_valid()
            and transp_to_form.is_valid()
            and (
                not machine_options_form
                or machine_options_form.is_valid()
                )
            ):
            transp_to_form.save()
            transp_out_form.save()
        else:
            context = self.get_context_data(
                form=self.get_form(),
                machine_options_form=machine_options_form,
                transp_to_form=transp_to_form,
                transp_out_form=transp_out_form,
                )
            return self.render_to_response(context, status=400)

        return super().post(request, *args, **kwargs)

    def serrialize_request_key(self, key: str) -> dict:
        data = self.request.POST.get(key)
        request_serrialized = {}
        if data:
            for i in data.split(','):
                if i: j, k = i.split('=')
                if j: request_serrialized[j] = k
        request_serrialized.pop('csrfmiddlewaretoken', None)
        return request_serrialized

    def get_another_form(self, instance, key: str) -> Form:
        data = self.serrialize_request_key(key)
        data['content_type_id'] = ContentType.objects.get_for_model(self.object.__class__).id
        data['object_id'] = self.object.id
        form = getattr(self, key)(instance=instance, data=data)
        return form

    def get_machine_options_form(self, request) -> Form or None:
        if 'machine_options_form' in request.POST:
            machine_options_form = MachineTypeForm.options_constructor(
                ContentType.objects.get_for_id(request.POST['machine_type']).model_class()
                )(self.serrialize_request_key('machine_options_form'))
            self.machine_options_form = machine_options_form
            return machine_options_form
        else:
            return None



class UpdateOrder(MultiFormMixin, UpdateView):

    model = Order
    form_class = OrderForm
    success_url = '/orders/'
    extra_context = {'id': 'update_order_form'}

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'header': self.object._meta.verbose_name + ' ' + str(self.object.pk),
            'href': self.request.get_full_path(),
            })
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('type', None) == 'delete':
            order = self.get_object()
            application = order.to_application().copy()
            application.update({'renouncement': False})
            try:
                order.delete()
            except DeleteError:
                return JsonResponse(
                    {'error': 'Невозможно удалить заказ, содержащий документы.'},
                    status=400)
            Application(**application).save()
            return redirect(self.success_url)
        else:
            return super().post(request, *args, **kwargs)


class UpdateApplication(MultiFormMixin, UpdateView):

    model = Application
    form_class = ApplicationForm
    success_url = '/applications/'
    extra_context = {'id': 'update_app_form'}

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'header': self.object._meta.verbose_name + ' ' + str(self.object.pk),
            'href': self.request.get_full_path(),
            })
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        if request.POST.get('renouncement', None) == 'false':
            object.renouncement = False
            object.save()
            self.object = object
            messages.success(request, self.get_success_message())
            return redirect(self.success_url)
        else:
            return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.renouncement = None
        return super().form_valid(form)


class CreateApplication(MultiFormMixin, CreateView):

    model = Application
    form_class = ApplicationForm
    extra_context = {'header': 'Новая заявка', 'href': reverse_lazy('applications_new'), 'id': 'new_app_form'}
    success_url = '/applications/'

    def get_context_data(self, **kwargs):
        self.extra_context.update({
            'transp_to_form': kwargs.get('transp_to_form') or self.transp_to_form(),
            'transp_out_form': kwargs.get('transp_out_form') or self.transp_out_form(),
            'machine_options_form': kwargs.get('machine_options_form') or self.machine_options_form,
            })
        return super(CreateView, self).get_context_data(**kwargs)

    def get_object(self, queryset=None) -> models.Model or None:
        return getattr(self, 'object', None)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            #Чтобы заявка не ушла в заказ до прикрепления доставок (костыль)
            start_date = form.instance.start_date
            form.instance.start_date = date.today() + timedelta(days=1)

            self.object = form.save()
            try:
                machine_options_form = self.get_machine_options_form(request)
                transp_to_form = self.get_another_form(self.object.transportation_to.first(), 'transp_to_form')
                transp_out_form = self.get_another_form(self.object.transportation_out.first(), 'transp_out_form')
                if transp_out_form.is_valid() and transp_to_form.is_valid():
                    transp_to_form.save()
                    transp_out_form.save()
                    self.object.start_date = start_date
                    self.object.save()
                    messages.success(request, self.get_success_message())
                    return redirect(self.success_url)
            except:
                self.object.delete()
                raise Exception
        context = self.get_context_data(
            form=form,
            machine_options_form=machine_options_form,
            transp_to_form=transp_to_form,
            transp_out_form=transp_out_form,
            )
        return self.render_to_response(context, status=400)


class CreateMachine(FormSet, CreateView):

    def setup(self, request, *args, **kwargs):
        for i in get_machine_types():
            if i.name() == kwargs['type']:
                self.model = i
                self.fields = [i for i in i.model_fields() if i !='in_work']
                self.success_url = reverse('machine_type', kwargs=kwargs)
                self.extra_context = {
                    'header': 'Добавить ' + i._meta.verbose_name,
                    'href': reverse('machine_new', kwargs=kwargs),
                    'id': 'new_machine_form',
                    }
                break
        else:
            raise Http404
        return super().setup(request, *args, **kwargs)


class CreatePartner(FormSet, CreateView):

    form_class = PartnerForm
    extra_context = {'header': 'Новый контрагент', 'href': reverse_lazy('partners_new'), 'id': 'new_partner_form'}
    success_url = '/partners/'


class CreateEntity(OnlyAjaxResponseMixin, CreateView):

    model = Entity
    fields = ['inn']
    template_name = 'mainapp/partners.html'
    success_url = '/partners/'
    http_method_names = ['post']

    def form_valid(self, form):
        form.instance.partner = Partner.objects.get(**self.kwargs)
        form.instance.save()
        return JsonResponse({'name': form.instance.name, 'inn': form.instance.inn, 'id': form.instance.id})

    def form_invalid(self, form):
        return JsonResponse({'error': 'Ошибка в ИНН'}, status=400)

    def post(self, request, *args, **kwargs):
        if request.POST.get('type', None) == 'delete':
            try:
                self.get_object().delete()
            except (DeleteError, ValidationError, ProtectedError):
                return JsonResponse({'error': 'Юр. лицо имеет заказ или заявку'}, status=500)
            return JsonResponse({})
        return super().post(request, *args, **kwargs)


class UpdateWorkshifts(OnlyAjaxResponseMixin, UpdateView):

    model = WorkShift
    success_url = '/orders/'

    def form_valid(self, form):
        super().form_valid(form)
        statistics = Statistics(
            Q(order=self.object.order),
            self.object.order.start_date,
            self.object.order.end_date
            ).full()
        return JsonResponse(statistics | {
                'this_icost': self.object.get_option_inc_cost() + self.object.order.incoming_cost,
                'this_ocost': self.object.get_option_out_cost() + self.object.order.outdoing_cost
            })

    def setup(self, request, *args, **kwargs):
        self.fields = [key for key in request.POST.keys()]
        return super().setup(request, *args, **kwargs)

    def form_invalid(self, form):
        return JsonResponse({
            key: localize(value)
            for key, value in WorkShift.objects.get(id=form.instance.id).__dict__.items()
            if key != '_state'
            }, status=400)


class MachineOptionsForm(FormView):

    template_name = 'mainapp/machine_options_form.html'
    http_method_names = ['get']

    def setup(self, request, *args, **kwargs):
        try:
            self.form_class = MachineTypeForm.options_constructor(
                ContentType.objects.get_for_id(kwargs['machine_type_id']).model_class()
                )
        except KeyError:
            raise Http404

        if 'content_type' in kwargs and 'object_id' in kwargs:
            if kwargs['content_type'] == 'application':
                content_type = Application
            elif kwargs['content_type'] == 'order':
                content_type = Order
            else:
                raise Http404

            options = content_type.objects.get(id=kwargs['object_id']).options
            if options: self.initial.update(**options)

        return super().setup(request, *args, **kwargs)


def datetimeinfo(request):
    if request.is_ajax():
        return JsonResponse({'date': datetime.now().strftime('%d.%m.%Y'), 'time': datetime.now().time()})
    else:
        raise Http404

def home(request):
    return redirect(reverse('applications'), permanent=True)

def statistics(request):
    return redirect(reverse('applications'), permanent=True)
