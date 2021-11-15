from django.contrib import admin

from .models import City, Record


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'date', 'temperature', 'wind_direction',
                    'wind_speed', 'status', 'precipitation')
    search_fields = ('city', 'date', 'status')
    list_filter = ('city', 'date', 'status')
    empty_value_display = '---'
