from django.db import models


class City(models.Model):
    name = models.CharField('Название', max_length=50)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name


class Record(models.Model):
    """
    Model for recording a weather station about the current state
    of the weather
    """
    city = models.ForeignKey(City, verbose_name='Город', max_length=50,
                             on_delete=models.CASCADE,
                             related_name='city_record')
    date = models.DateTimeField('Дата и время')
    temperature = models.FloatField('Температура', null=True)
    wind_direction = models.FloatField('Направление ветра в градусах',
                                       null=True)
    wind_speed = models.IntegerField('Скорость ветра в м/с')
    status = models.CharField('Погода', max_length=50, null=True)
    precipitation = models.FloatField('Атмосферные осадки в мм')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        constraints = [
            models.UniqueConstraint(
                fields=['city', 'date'],
                name='unique_city_date',
            )
        ]
