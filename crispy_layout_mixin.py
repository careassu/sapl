from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Fieldset, Layout, Submit
from django import forms
from django.utils.translation import ugettext as _


def to_column(name_span):
    fieldname, span = name_span
    return Div(fieldname, css_class='col-md-%d' % span)


def to_row(names_spans):
    return Div(*map(to_column, names_spans), css_class='row-fluid')


def to_fieldsets(fields):
    for field in fields:
        if isinstance(field, list):
            legend, *row_specs = field
            rows = [to_row(name_span_list) for name_span_list in row_specs]
            yield Fieldset(legend, *rows)
        else:
            yield field


def form_actions(more=[], save_label=_('Salvar')):
    return FormActions(
        Submit('salvar', save_label, css_class='pull-right'), *more)


class SaplFormLayout(Layout):

    def __init__(self, *fields):
        buttons = form_actions(more=[
            HTML('<a href="{{ view.cancel_url }}"'
                 ' class="btn btn-inverse">%s</a>' % _('Cancelar'))])
        _fields = list(to_fieldsets(fields)) + [to_row([(buttons, 12)])]
        super(SaplFormLayout, self).__init__(*_fields)


def get_field_display(obj, fieldname):
    field = obj._meta.get_field(fieldname)
    verbose_name = str(field.verbose_name)
    if field.choices:
        value = getattr(obj, 'get_%s_display' % fieldname)()
    else:
        value = getattr(obj, fieldname)
    if value is None:
        display = ''
    elif 'date' in str(type(value)):
        display = value.strftime("%d/%m/%Y")  # TODO: localize
    elif 'bool' in str(type(value)):
        display = 'Sim' if value else 'Não'
    else:
        display = str(value)
    return verbose_name, display


class CrispyLayoutFormMixin(object):

    def get_form_class(self):

        layout = self.layout

        class CrispyForm(forms.ModelForm):

            class Meta:
                model = self.model
                exclude = []

            def __init__(self, *args, **kwargs):
                super(CrispyForm, self).__init__(*args, **kwargs)
                self.helper = FormHelper()
                self.helper.layout = SaplFormLayout(*layout)

        return CrispyForm

    @property
    def list_field_names(self):
        '''The list of field names to display on table

        This base implementation returns the field names
        in the first fieldset of the layout.
        '''
        rows = self.layout[0][1:]
        return [fieldname for row in rows for fieldname, __ in row]

    def get_column(self, fieldname, span):
        obj = self.get_object()
        verbose_name, text = get_field_display(obj, fieldname)
        return {
            'id': fieldname,
            'span': span,
            'verbose_name': verbose_name,
            'text': text,
        }

    @property
    def layout_display(self):
        return [
            {'legend': legend,
             'rows': [[self.get_column(fieldname, span)
                       for fieldname, span in row]
                      for row in rows]
             } for legend, *rows in self.layout]
