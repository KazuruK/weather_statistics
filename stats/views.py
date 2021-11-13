import csv
import datetime as dt
import os

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StatisticForm
from .models import City, Record
from .utils import get_statistics


def load_data(request):
    temp_data = []
    object_id = (Record.objects.latest('id').id + 1
                 if Record.objects.all().exists()
                 else 0)
    for filename in os.listdir(settings.LOAD_DATA_DIR):
        city, created = City.objects.get_or_create(name=filename[:-4])
        with open(
                f'{settings.LOAD_DATA_DIR}/{filename}',
                encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[1] != '':
                    continue
                temp_data.append(Record(
                    id=object_id,
                    city=city,
                    date=dt.datetime.strptime(row[0], "%d.%m.%Y %H:%M"),
                    temperature=float(row[1]),
                    wind_direction=float(row[2]) if row[2] != '' else None,
                    wind_speed=int(row[3]) if row[3] != '' else 0,
                    status=row[4] if row[4] != '' else None,
                    precipitation=float(row[5])
                ))
                object_id += 1
    Record.objects.bulk_create(temp_data, batch_size=999)
    return redirect('stats:index')


def index(request):
    form = StatisticForm(request.POST or None)
    if form.is_valid():
        form = form.cleaned_data
        city = get_object_or_404(City, id=form['city'])
        start = form['start_date']
        end = form['end_date'] + dt.timedelta(days=1)
        records = city.city_record.filter(date__range=(start, end))
        statistic = get_statistics(
            records,
            (end - start).days > 730,
            city.name
        )
        return render(request, 'stats/statistic.html', {
            'start_date': form['start_date'],
            'end_date': form['end_date'],
            'city': city.name,
            'period_temp_min': statistic[0],
            'period_temp_max': statistic[1],
            'period_temp_avg': statistic[2],
            'years_stats': statistic[3],
            'close_date': statistic[4],
            'clear_days': statistic[5],
            'frequent_prec': statistic[6],
            'wind_direction_avg': statistic[7],
            'wind_speed_avg': statistic[8],
            'records_count': records.count()
        })
    return render(request, 'stats/index.html', {'form': form})
