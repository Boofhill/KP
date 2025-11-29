from django.db import models
from django.contrib.auth.models import User


class Filial(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название филиала")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название должности")
    department = models.CharField(max_length=100, verbose_name="Отдел")

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, verbose_name="Филиал")
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Должность")
    photo = models.ImageField(upload_to='employees/', blank=True, null=True, verbose_name="Фотография")
    birth_date = models.DateField(verbose_name="Дата рождения")
    internal_phone = models.CharField(max_length=6, unique=True, verbose_name="Внутренний телефон")
    is_smus = models.BooleanField(default=False, verbose_name="Является членом СМУС")

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class SMUS(models.Model):
    POSITIONS = [
        ('predsedatel', 'Председатель'),
        ('zamestitel', 'Заместитель'),
        ('chlen', 'Член совета'),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    position = models.CharField(max_length=20, choices=POSITIONS, verbose_name="Должность в СМУС")

    class Meta:
        verbose_name = 'Член СМУС'
        verbose_name_plural = 'Члены СМУС'

    def __str__(self):
        return f"{self.employee} - {self.get_position_display()}"


class Event(models.Model):
    DIRECTIONS = [
        ('science', 'Научная деятельность'),
        ('sport', 'Спортивные мероприятия'),
        ('culture', 'Культурные мероприятия'),
        ('education', 'Образовательные мероприятия'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название мероприятия")
    description = models.TextField(verbose_name="Описание")
    date = models.DateField(verbose_name="Дата проведения")
    direction = models.CharField(max_length=20, choices=DIRECTIONS, verbose_name="Направление")
    year = models.CharField(max_length=4, default='2024', verbose_name="Год")
    creator = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Создатель")

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return self.name


class Participation(models.Model):
    ROLES = [
        ('participation', 'Участие (0.1 балла)'),
        ('curator', 'Кураторство (0.2 балла)'),
        ('creator', 'Создание (0.3 балла)'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Мероприятие")
    role = models.CharField(max_length=20, choices=ROLES, verbose_name="Степень участия")

    class Meta:
        unique_together = ['employee', 'event']
        verbose_name = 'Участие'
        verbose_name_plural = 'Участия'

    def get_points(self):
        from decimal import Decimal
        points = {
            'participation': Decimal('0.1'),
            'curator': Decimal('0.2'),
            'creator': Decimal('0.3')
        }
        return points.get(self.role, Decimal('0'))

class SMUSRating(models.Model):
    smus = models.ForeignKey(SMUS, on_delete=models.CASCADE, verbose_name="Член СМУС")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Мероприятие")
    score = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="Оценка")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        unique_together = ['smus', 'event']
        verbose_name = 'Оценка СМУС'
        verbose_name_plural = 'Оценки СМУС'

    def __str__(self):
        return f"{self.smus} - {self.event}: {self.score}"