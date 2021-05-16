from django.db.models import Model, CharField, PositiveIntegerField, BooleanField, DateField, ForeignKey, CASCADE
from transliterate import translit
from django.core.management import call_command
from importlib import import_module, reload
from django.conf import settings
from django.urls import clear_url_caches
from datetime import date
from mainapp.models import Partner # type: ignore
import codecs


class Machine(Model):

    partner = ForeignKey(Partner, on_delete=CASCADE, verbose_name='Контрагент')
    label = CharField(verbose_name='Марка', max_length=30, blank=True)
    in_work = DateField(verbose_name='В работе', blank=True, null=True)

    class Meta:

        ordering = ['-id']
        abstract = True

    def __str__(self):
        return self._meta.verbose_name

    def clean(self) -> None:
        if self.in_work and self.in_work < date.today():
            self.in_work = None
        return super().clean()

    @classmethod
    def name(cls):
        name = cls.__name__
        if name[-7:] == 'dynamic':
            name = name[:-7].lower()
        return name

    @classmethod
    def url(cls):
        name = cls.name()
        url = f'/machine/{name}/'
        return url

    @classmethod
    def model_fields(cls):
        return {i.name: i.verbose_name for i in cls._meta.get_fields() if i.name not in (
            'id',
            '_state',
            )}

    @classmethod
    def search_fields(cls):
        return ['partner', 'label']

    @classmethod
    def type_fields(cls):
                return {i.name: i for i in cls._meta.get_fields() if i.name not in (
            'id',
            '_state',
            'in_work',
            )}

    @classmethod
    def get_options(cls):
        return [(i.name, i.verbose_name) for i in cls._meta.fields if isinstance(i, BooleanField)]


def get_machine_types():
    return sorted([i for i in Machine.__subclasses__()], key=lambda x: x._meta.verbose_name)


class CRUDModel:

    _abc = {'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm'}
    sufix = 'dynamic'
    admin_name = ''
    template = Machine
    short_name = None
    attrs = {}
    new_class_attrs = {}

    def str_to_var(self, string):
        new_string = ''

        try:
            string = translit(string, reversed=True)
        except:
            pass

        for i in string.lower():
            if i in self._abc:
                new_string += i

        if not new_string:
            raise Exception(f'Недопустимое название {string}')

        new_string += self.sufix
        return new_string

    def str_to_classname(self, string):
        name = self.str_to_var(string).capitalize()
        from .models import __dict__ as D
        if D.get(name, None) is None:
            self.classname = name
            return name
        else:
            raise Exception(f'{name} уже существует')

    def class_name(self, name):
        return f'\n\nclass {name}({self.template.__name__}):\n\n'

    def class_attrs(self, **kwargs):
        attrs = {}
        str_attr = ''
        for key, value in kwargs.items():
            var_key = self.str_to_var(key)

            if var_key in vars(self.template):
                raise Exception(f'Имя {var_key} зарезервированно в шаблоне {self.template.__name__}')

            if value == 'int':
                str_attr += f'    {var_key} = PositiveIntegerField(verbose_name="{key}", blank=True, null=True)\n'
                attrs.update({var_key: PositiveIntegerField(verbose_name=key, blank=True, null=True)})
            elif value == 'bool':
                str_attr += f'    {var_key} = BooleanField(verbose_name="{key}", default=None, null=True)\n'
                attrs.update({var_key: BooleanField(verbose_name=key, default=None, null=True)})
            elif value == 'char':
                str_attr += f'    {var_key} = CharField(max_length=30, verbose_name="{key}", blank=True)\n'
                attrs.update({var_key: CharField(max_length=30, verbose_name=key, blank=True)})
            else:
                raise Exception(f'Недопустимый формат поля "{value}"')

        self.new_class_attrs.update(attrs)
        return str_attr

    def class_meta(self):
        if self.short_name:
            verb_name = self.short_name
        else:
            verb_name = self.name

        class Meta:
            verbose_name = verb_name
            verbose_name_plural = verb_name

        self.new_class_attrs['Meta'] = Meta
        return f'\n    class Meta:\n        verbose_name = "{verb_name}"\n        verbose_name_plural = "{verb_name}"\n'


class CreateModel(CRUDModel):

    def __init__(self, register_admin=True, **kwargs):

        for key, value in kwargs.items():

            if not value:
                continue
            elif key == 'name':
                self.name = value
            elif key == 'short_name':
                self.short_name = value
            elif key[:4] == 'prop':
                self.attrs[value] = 'int'
            elif key[:7] == 'options':
                self.attrs[value] = 'bool'
            else:
                raise Exception('Недопустимые параметры техники')

        self.register_admin = register_admin
        self.get_class()

    def get_class(self):
        name = self.str_to_classname(self.name)
        str_class = self.class_name(name)
        str_class += self.class_attrs(**self.attrs)
        str_class += self.class_meta()

        self.new_class_attrs['__module__'] = 'machines.models'
        new_class = type(name, (self.template,), self.new_class_attrs)

        self.new_class = new_class
        self.str_class = str_class

    def write_class(self):
        with codecs.open('machines/models.py', 'a', encoding='utf-8') as f:
            f.write(self.str_class)
        call_command('makemigrations')
        call_command('migrate')
        if self.admin_name:
            admin_name = ', ' + self.admin_name
        else:
            admin_name = ''
        if self.register_admin:
            with open('machines/admin.py', 'ta') as f:
                f.write(f'admin.site.register({self.str_to_classname(self.name) + admin_name})\n')
        reload(import_module(settings.ROOT_URLCONF))
        clear_url_caches()


class UpdateModel(CRUDModel):

    def __init__(self, model_name, **kwargs):
        for key, value in kwargs.items():

            if not value:
                continue
            if key == 'short_name':
                self.short_name = value
            elif key[:4] == 'prop':
                self.attrs[value] = 'int'
            elif key[:7] == 'options':
                self.attrs[value] = 'bool'
            else:
                raise Exception('Недопустимые параметры техники')

        self.updated_class = self.get_updated_class(model_name)

    def get_updated_class(self, model_name):
        from .models import __dict__ as D
        updated_class = D.get(model_name, None)
        if updated_class is None:
            raise Exception(f'Модель {model_name} не найдена')
        else:
            return updated_class

    def get_new_text(self):
        name = self.updated_class.__name__
        with codecs.open('machines/models.py', 'r', encoding='utf-8') as f:
            found = False
            old_class = ''
            for line in f:

                if found:
                    if line.startswith('class'):
                        break
                    else:
                        old_class += line
                else:
                    if line.startswith(f'class {name}'):
                        found = True

            f.seek(0)
            text = f.read()

        new_class = '\n' + self.class_attrs(**self.attrs) + self.class_meta() +'\n\n'
        return text.replace(old_class, new_class, 1)

    def update_class(self):
        text = self.get_new_text()
        for key in self.updated_class.__dict__.copy().keys():
            if key.endswith(self.sufix):
                delattr(self.updated_class, key)
        for key, value in self.new_class_attrs.items():
            if key != 'Meta':
                setattr(self.updated_class, key, value)
        self.updated_class._meta.verbose_name = self.short_name
        self.updated_class._meta.verbose_name_plural = self.short_name
        with codecs.open('machines/models.py', 'w', encoding='utf-8') as f:
            f.write(text)
        reload(import_module('machines.models'))
        call_command('makemigrations')
        call_command('migrate')
        reload(import_module(settings.ROOT_URLCONF))
        clear_url_caches()


# -----------------------------------Dynamic models---------------------------------


class Ekskavatorpogruzchikdynamic(Machine):

    gidromolotdynamic = BooleanField(verbose_name="Гидромолот", default=None, null=True)
    plankovshdynamic = BooleanField(verbose_name="План. ковш", default=None, null=True)
    uzkijkovshdynamic = BooleanField(verbose_name="Узкий ковш", default=None, null=True)
    vilydynamic = BooleanField(verbose_name="Вилы", default=None, null=True)
    ravnokolesnyjdynamic = BooleanField(verbose_name="Равно-колесный", default=None, null=True)

    class Meta:
        verbose_name = "ЭП"
        verbose_name_plural = "ЭП"


class Gusenichnyjekskavatordynamic(Machine):

    vesdynamic = PositiveIntegerField(verbose_name="Вес", blank=True, null=True)
    shirinagusenitsdynamic = PositiveIntegerField(verbose_name="Ширина гусениц", blank=True, null=True)
    dlinnastrelydynamic = PositiveIntegerField(verbose_name="Длинна стрелы", blank=True, null=True)
    gidromolotdynamic = BooleanField(verbose_name="Гидромолот", default=None, null=True)
    plankovshdynamic = BooleanField(verbose_name="План. ковш", default=None, null=True)
    uzkijkovshdynamic = BooleanField(verbose_name="Узкий ковш", default=None, null=True)

    class Meta:
        verbose_name = "ЭГ"
        verbose_name_plural = "ЭГ"


class Shalandadynamic(Machine):

    dlinnadynamic = PositiveIntegerField(verbose_name="Длинна", blank=True, null=True)
    gruzopodemnostdynamic = PositiveIntegerField(verbose_name="Грузоподъемность", blank=True, null=True)
    konikidynamic = BooleanField(verbose_name="Коники", default=None, null=True)
    vezdehoddynamic = BooleanField(verbose_name="Вездеход", default=None, null=True)

    class Meta:
        verbose_name = "АБ"
        verbose_name_plural = "АБ"


class Minipogruzchikdynamic(Machine):

    vesdynamic = PositiveIntegerField(verbose_name="Вес", blank=True, null=True)
    gruzopodemnostdynamic = PositiveIntegerField(verbose_name="Грузоподъемность", blank=True, null=True)
    gidromolotdynamic = BooleanField(verbose_name="Гидромолот", default=None, null=True)
    vilydynamic = BooleanField(verbose_name="Вилы", default=None, null=True)
    schetkadynamic = BooleanField(verbose_name="Щетка", default=None, null=True)
    gusenichnyjdynamic = BooleanField(verbose_name="Гусеничный", default=None, null=True)

    class Meta:
        verbose_name = "МП"
        verbose_name_plural = "МП"


class Samosvaldynamic(Machine):

    vesdynamic = PositiveIntegerField(verbose_name="Вес", blank=True, null=True)
    obemdynamic = PositiveIntegerField(verbose_name="Объем", blank=True, null=True)
    gruzopodemnostdynamic = PositiveIntegerField(verbose_name="Грузоподъемность", blank=True, null=True)
    vezdehoddynamic = BooleanField(verbose_name="Вездеход", default=None, null=True)

    class Meta:
        verbose_name = "СС"
        verbose_name_plural = "СС"




class Avtokrandynamic(Machine):

    gruzopodemnostdynamic = PositiveIntegerField(verbose_name="Грузоподъемность", blank=True, null=True)
    dlinnastrelydynamic = PositiveIntegerField(verbose_name="Длинна стрелы", blank=True, null=True)

    class Meta:
        verbose_name = "АК"
        verbose_name_plural = "АК"
