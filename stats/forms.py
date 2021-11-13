import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import City


class StatisticForm(forms.Form):
    class Meta:
        fields = ('city', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        years_range = range(datetime.date.today().year, 2009, -1)
        cities = City.objects.values_list('id', 'name')
        self.fields['city'] = forms.ChoiceField(
            choices=(*cities,),
            label='Город'
        )
        self.fields['start_date'] = forms.DateTimeField(
            label='Начало периода',
            help_text='Данная дата должна быть меньше',
            widget=forms.SelectDateWidget(
                years=years_range
            ))
        self.fields['end_date'] = forms.DateTimeField(
            label='Конец периода',
            help_text='Данная дата должна быть больше',
            widget=forms.SelectDateWidget(
                years=years_range
            ))

    def clean(self):
        cleaned_data = super(StatisticForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date >= end_date:
            err = ValidationError(
                'Неверный формат дат! Убедитесь что временной '
                'промежуток указан верно'
            )
            self.add_error('start_date', err)
            self.add_error('end_date', err)
        return cleaned_data
