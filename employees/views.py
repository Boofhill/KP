from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from django.contrib.auth.decorators import login_required  # Добавляем импорт
from .models import Employee, Event, SMUS, SMUSRating, Participation


# Главная страница - доступна всем
def glavnaya(request):
    employees_count = Employee.objects.count()
    events_count = Event.objects.count()

    return render(request, 'glavnaya.html', {
        'employees_count': employees_count,
        'events_count': events_count
    })


# Все остальные страницы защищаем авторизацией
@login_required
def sotrudniki(request):
    employees = Employee.objects.all()
    return render(request, 'sotrudniki.html', {'employees': employees})


@login_required
def meropriyatiya(request):
    events = Event.objects.all().annotate(
        srednyaya_ocenka=Avg('smusrating__score')
    )
    return render(request, 'meropriyatiya.html', {'events': events})


@login_required
def smus(request):
    members = SMUS.objects.all()
    return render(request, 'smus.html', {'smus': members})


@login_required
def ocenki_meropriyatiya(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ratings = SMUSRating.objects.filter(event=event)
    srednyaya_ocenka = ratings.aggregate(Avg('score'))['score__avg'] or 0

    return render(request, 'ocenki_meropriyatiya.html', {
        'event': event,
        'ratings': ratings,
        'srednyaya_ocenka': srednyaya_ocenka
    })


@login_required
def reiting(request):
    rating_data = []

    for employee in Employee.objects.all():
        participations = Participation.objects.filter(employee=employee)
        itogovy_ball = 0
        kolichestvo_meropriyatiy = participations.count()

        for participation in participations:
            event = participation.event
            srednyaya_ocenka = SMUSRating.objects.filter(
                event=event
            ).aggregate(Avg('score'))['score__avg'] or 0

            ball_uchastiya = participation.get_points()
            itogovy_ball += srednyaya_ocenka * ball_uchastiya

        if kolichestvo_meropriyatiy > 0:
            rating_data.append({
                'employee': employee,
                'itogovy_ball': round(itogovy_ball, 2),
                'kolichestvo_meropriyatiy': kolichestvo_meropriyatiy
            })

    rating_data.sort(key=lambda x: x['itogovy_ball'], reverse=True)

    return render(request, 'reiting.html', {'rating': rating_data})