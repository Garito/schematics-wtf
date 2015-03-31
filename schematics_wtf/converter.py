"""
Tools for generating forms based on Schematics Models
"""
import datetime
from operator import itemgetter
from schematics.models import Model
from schematics.transforms import wholelist, whitelist, blacklist
from wtforms import fields as f, validators, Form, ValidationError
from wtforms.fields import html5 as html5f
from wtforms.widgets import HiddenInput, TextInput

def converts(*args):
    def _inner(func):
        func._converter_for = frozenset(args)
        return func
    return _inner


def date_format(date_format):
    message = 'Date string must match {}.'.format(date_format)
    def _format(form, field):
        if not isinstance(field.data, basestring):
           raise ValidationError(message)
        try:
            value = time.strptime(field.data, date_format)[:3]
            value = datetime.date(*value)
        except:
            raise ValidationError(message)
    return _format

def time_format(time_format):
    message = 'Time string must match {}.'.format(time_format)
    def _format(form, field):
        if not isinstance(field.data, basestring):
           raise ValidationError(message)
        try:
            value = time.strptime(field.data, time_format)[3:5]
            value = datetime.time(*value)
        except:
            raise ValidationError(message)
    return _format


class ModelConverter(object):

    def __init__(self, converters=None):

        if not converters:
            converters = {}

        for name in dir(self):
            obj = getattr(self, name)
            if hasattr(obj, '_converter_for'):
                for classname in obj._converter_for:
                    converters[classname] = obj

        self.converters = converters

    def convert(self, model, field, field_name, field_args, hidden=False):
        kwargs = {
            'label': getattr(field, 'form_name', field_name),
            'description': '',
            'validators': [],
            'filters': [],
            'default': field.default,
        }

        if hidden:
           kwargs['widget'] = HiddenInput()

        if model._data[field_name]:
           kwargs['default'] = model._data[field_name]

        if field_args:
           kwargs.update(field_args)

        if field.required:
           kwargs['validators'].append(validators.Required())
        else:
           kwargs['validators'].append(validators.Optional())

        if field.choices:
           choices = [(x,x) for x in field.choices]
           kwargs['choices'] = choices
           if kwargs.pop('multiple', False):
               return f.SelectMultipleField(**kwargs)
           return f.SelectField(**kwargs)

        ftype = type(field).__name__

        if hasattr(field, 'to_form_field'):
           return field.to_form_field(model, kwargs)

        if ftype in self.converters:
           return self.converters[ftype](model, field, kwargs)

    @classmethod
    def _string_common(cls, model, field, kwargs):
        if field.max_length or field.min_length:
            kwargs['validators'].append(
                validators.Length(max=field.max_length or - 1,
                                  min=field.min_length or - 1))

    @classmethod
    def _number_common(cls, model, field, kwargs):
        if field.max_value or field.min_value:
            kwargs['validators'].append(
                validators.NumberRange(max=field.max_value,
                                       min=field.min_value))

    @converts('StringType')
    def conv_String(self, model, field, kwargs):
        if field.regex:
            kwargs['validators'].append(validators.Regexp(regex=field.regex))
        self._string_common(model, field, kwargs)
        if 'password' in kwargs:
            if kwargs.pop('password'):
                return f.PasswordField(**kwargs)
        if 'textarea' in kwargs:
            if kwargs.pop('textarea'):
                return f.TextAreaField(**kwargs)
        if 'file' in kwargs:
            if kwargs.pop('file'):
                return f.FileField(**kwargs)
        return f.StringField(**kwargs)

    @converts('URLType')
    def conv_URL(self, model, field, kwargs):
        kwargs['validators'].append(validators.URL())
        self._string_common(model, field, kwargs)
        return f.StringField(**kwargs)

    @converts('EmailType')
    def conv_Email(self, model, field, kwargs):
        kwargs['validators'].append(validators.Email())
        self._string_common(model, field, kwargs)
        return html5f.EmailField(**kwargs)

    @converts('IntType')
    def conv_Int(self, model, field, kwargs):
        self._number_common(model, field, kwargs)
        return html5f.IntegerField(**kwargs)

    @converts('FloatType')
    def conv_Float(self, model, field, kwargs):
        self._number_common(model, field, kwargs)
        return html5f.DecimalField(**kwargs)

    @converts('DecimalType')
    def conv_Decimal(self, model, field, kwargs):
        self._number_common(model, field, kwargs)
        return html5f.DecimalField(**kwargs)

    @converts('BooleanType')
    def conv_Boolean(self, model, field, kwargs):
        return f.BooleanField(**kwargs)

    @converts('DateTimeType')
    def conv_DateTime(self, model, field, kwargs):
        #return f.DateTimeField(**kwargs)
        if 'js_format' in kwargs:
            field.js_format = kwargs.pop('js_format')
        return html5f.DateTimeField(**kwargs)

    @converts('DateType')
    def conv_Date(self, model, field, kwargs):
        if 'format' not in kwargs:
            kwargs['format'] = field.formats[0]
            
        #kwargs['validators'].append(date_format(kwargs['format']))
        return html5f.DateField(**kwargs)

    @converts('TimeType')
    def conv_Time(self, model, field, kwargs):
        kwargs['format'] = field.serialized_format
        kwargs['validators'].append(time_format(field.serialized_format))
        return html5f.DateTimeField(**kwargs)

    @converts('BinaryType')
    def conv_Binary(self, model, field, kwargs):
        #TODO: may be set file field that will save file`s data to MongoDB
        if field.max_bytes:
            kwargs['validators'].append(validators.Length(max=field.max_bytes))
        return f.TextAreaField(**kwargs)

    @converts('DictType')
    def conv_Dict(self, model, field, kwargs):
        return DictField(**kwargs)

    @converts('ListType')
    def conv_List(self, model, field, kwargs):
        if isinstance(field.field, ReferenceField):
            return ModelSelectMultipleField(model=field.field.document_type, **kwargs)
        if field.field.choices:
            kwargs['multiple'] = True
            return self.convert(model, field.field, kwargs)
        unbound_field = self.convert(model, field.field, {})
        kwargs = {
            'validators': [],
            'filters': [],
        }
        return f.FieldList(unbound_field, min_entries=0, **kwargs)

    @converts('SortedListType')
    def conv_SortedList(self, model, field, kwargs):
        #TODO: sort functionality, may be need sortable widget
        return self.conv_List(model, field, kwargs)

    @converts('GeoLocationType')
    def conv_GeoLocation(self, model, field, kwargs):
        #TODO: create geo field and widget (also GoogleMaps)
        return

    @converts('ModelType')
    def conv_EmbeddedDocument(self, model, field, kwargs):
        kwargs = {
            'validators': [],
            'filters': [],
        }
        form_class = model_form(field.document_type_obj, field_args={})
        return f.FormField(form_class, **kwargs)

    @converts('ReferenceField')
    def conv_Reference(self, model, field, kwargs):
        return ModelSelectField(model=field.document_type, **kwargs)

    @converts('GenericReferenceField')
    def conv_GenericReference(self, model, field, kwargs):
        return

#
# Bootstrap Model Converters
#

from schematics.types import StringType, IntType, BooleanType

class BootstrapTimePickerOptions(Model):
    template = StringType(choices=['dropdown', 'modal', 'false'], default='dropdown')
    minuteStep = IntType(choices=[1,2,3,4,5,6,10,12,15,20,30], default=15)
    secondsStep = IntType(default=15, min_value=1, max_value=30)
    showSeconds = BooleanType(default=False)
    defaultTime = StringType(default='current')
    showMeridian = BooleanType(default=True)
    showInputs = BooleanType(default=True)
    disableFocus = BooleanType(default=False)
    modalBackdrop = BooleanType(default=False)

    def __unicode__(self):
        for field in self._fields:
            pass
        return u""

class BootstrapTimePickerWidget(TextInput):
    def __init__(self, options=None):
        self.options = options or BootstrapTimePickerOptions()
        self.ver = self.options.pop('ver', 3)

    def __call__(self, field, **kwargs):
        if self.ver == 3:
            return u""" \
              <div class="input-group bootstrap-timepicker">
               <span class="input-group-addon"><span class="glyphicon glyphicon-time"></span></span>
               <input class="timepicker form-control" type="text" {options} value="{date}">
              </div>
            """.format(options=unicode(self.options))
        else:
            return u""" \
                <input type="hidden" {options} value="{date}">
                <div class="bootstrap-timepicker"></div>
            """.format(options=unicode(self.options))

class BootstrapDatePickerWidget(TextInput):
    js_format = 'YYYY-MM-DD'
    format = 'Y%-M%-D%'
    primitive_format = "%Y-%m-%dT%H:%M:%S.%f"
    
    def __init__(self, js_format=None, format=None, primitive_format=None, ver=None):
        if js_format:
            self.js_format = js_format
            
        if format:
            self.format = format
            
        if primitive_format:
            self.primitive_format

        self.ver = 3 if ver is None else ver
        
    def __call__(self, field, **kwargs):
        value = kwargs.get('value', field._value())
        
        if value != '' and value != '00:00:00' and self.primitive_format != self.format:
            value = datetime.datetime.strptime(value, self.primitive_format).strftime(self.format)
        
        if self.ver == 3:
            return u""" \
              <div class="input-group date datepicker">
              <span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>
               <input class="form-control" type="text" data-date-format="{format}" name="{name}" id="{name}" data-date="{date}" value="{date}">
              </div>
            """.format(name=field.name, format=self.js_format, date=value)
        else:
            return u""" \
                <input type="hidden" data-date-format="{format}" name="{name}" id="{name}" data-date="{date}" value="{date}">
                <div class="row"><div class="col-xs-12">
                <div id="{name}widget" class="bootstrap-datepicker"></div>
                </div></div>
            """.format(name=field.name, format=self.js_format, date=value)

class BootstrapModelConverter(ModelConverter):
    
    @converts('DateTimeType')
    def conv_DateTime(self, model, field, kwargs):
        field = self.conv_Date(model, field, kwargs)
        return super(BootstrapModelConverter, self).conv_DateTime(model, field, kwargs)

    @converts('DateType')
    def conv_Date(self, model, field, kwargs):
        kwargs['widget'] = BootstrapDatePickerWidget(kwargs.pop('js_format', None), 
                                                     kwargs.get('format', None), 
                                                     kwargs.get('primitive_format', None),
                                                     kwargs.pop('ver', None))
        return super(BootstrapModelConverter, self).conv_Date(model, field, kwargs)

    @converts('TimeType')
    def conv_Time(self, model, field, kwargs):
        options = kwargs.pop('bootstrap-options', BootstrapTimePickerOptions())
        kwargs['widget'] = BootstrapTimePickerWidget(options)
        return super(BootstrapModelConverter, self).conv_Time(model, field, kwargs)

def model_fields(model, only=None, exclude=None, hidden=None, field_args=None, converter=None):
    """
    Generate a dictionary of fields for a given Django model.

    See `model_form` docstring for description of parameters.
    """
    from schematics.models import Model
    if not isinstance(model, Model):
        raise TypeError('model must be a schematics.Model schema')

    converter = converter or ModelConverter()
    field_args = field_args or {}
    gottago = wholelist()
    field_dict = { }

    if only:
       gottago = whitelist(*only)
    elif exclude:
       gottago = blacklist(*exclude)

    for field_name, field in model._fields.items():
       if gottago(field_name, None): continue
       ishidden = False
       if hidden:
          if field_name in hidden: ishidden=True

       form_field = converter.convert(model, field, field_name, field_args.get(field_name), hidden=ishidden)

       if form_field is not None:
          field_dict[field_name] = form_field

    from pprint import pprint
    #pprint(field_dict)
    return field_dict


def model_form(model, base_class=Form, only=None, exclude=None, hidden=None, field_args=None, converter=None):
    """
    Create a wtforms Form for a given Schematic Model schema::

        from schematics.wtf import model_form
        from myproject.myapp.schemas import MyModel
        MyForm = model_form(MyModel)

    :param model:
        A Schematics Model schema class
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments used
        to construct each field object.
    :param converter:
        A converter to generate the fields based on the model properties. If
        not set, ``ModelConverter`` is used.
    """
#   if field_args is None and m:
#      field_args = model._data
    import inspect
    if inspect.isclass(model):
       model = model()
    field_dict = model_fields(model, only, exclude, hidden, field_args, converter)
    field_dict['model_class'] = model
    return type(model.__class__.__name__ + 'Form', (base_class,), field_dict)
