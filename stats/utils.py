import requests
from django.db.models import Avg, Count, F, Func, Max, Min, QuerySet
from django.db.models.functions import TruncYear

WIND_DIRECTIONS = {
    360.0: 'Север',
    180.0: 'Юг',
    270.0: 'Запад',
    90.0: 'Восток',
    315.0: 'Северо-запад',
    45.0: 'Северо-восток',
    225.0: 'Юго-запад',
    135.0: 'Юго-восток',
    22.5: 'Северо-северо-восток',
    337.5: 'Северо-северо-запад',
    157.5: 'Юго-юго-восток',
    202.5: 'Юго-юго-запад',
    247.5: 'Западо-юго-запад',
    292.5: 'Западо-северо-запад',
    67.5: 'Востоко-северо-восток',
    112.5: 'Востоко-юго-восток',
}


def get_statistics(records: QuerySet, years_stats: bool, city: str):
    results = []
    [results.append(res) for res in get_temp_stats(records, years_stats, city)]
    [results.append(res) for res in get_prec_stats(records)]
    [results.append(res) for res in get_wind_stats(records)]
    return results


def get_temp_stats(records: QuerySet, two_year: bool, city: str):
    period_stats = records.aggregate(
        Min('temperature'),
        Max('temperature'),
        Avg('temperature')
    )
    if two_year:
        years_stats = (
            records.annotate(year=TruncYear('date'))
            .values('year')
            .annotate(min_year=Min('temperature'), max_year=Max('temperature'))
            .aggregate(Avg('min_year'), Avg('max_year'))
        )
    try:
        temp_today = float(requests.get(f'https://wttr.in/{city}?format=%t').text[:-2])
        close_date = records.only('temperature').annotate(abs_diff=Func(F('temperature') - temp_today, function='ABS')).order_by('abs_diff').first()
    except requests.exceptions.RequestException:
        close_date = None
    return (period_stats['temperature__min'], period_stats['temperature__max'],
            round(period_stats['temperature__avg'], 3),
            [round(years_stats['min_year__avg'], 3),
             round(years_stats['max_year__avg'], 3)] if two_year else None,
            close_date)


def get_prec_stats(records: QuerySet):
    frequent_prec = list(
        records.values('status')
        .annotate(cnt=Count('status'))
        .order_by('-cnt')
        .values_list('status', flat=True)
    )[:2]
    if None in frequent_prec:
        frequent_prec.remove(None)
    clear_days = round((records.filter(precipitation=0).count() /
                        records.count() * 100), 3)
    return clear_days, ', '.join(frequent_prec)


def get_wind_stats(records: QuerySet):
    average_stats = records.aggregate(Avg('wind_direction'), Avg('wind_speed'))
    direction = min(
        enumerate(list(WIND_DIRECTIONS.keys())),
        key=lambda x: abs(average_stats['wind_direction__avg'] - x[1])
    )[1]
    return WIND_DIRECTIONS[direction], round(average_stats['wind_speed__avg'], 3)
