from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin  # Добавлен UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Employee, Event, SMUS, SMUSRating, Participation
from .forms import EmployeeCreationForm, EmployeeUpdateForm
from decimal import Decimal
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Employee
from django.db.models import Count, Q
from django.shortcuts import render
from .models import Employee, Filial, Position

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
    # Получаем всех сотрудников с предзагрузкой связанных данных
    employees = Employee.objects.select_related('user', 'filial', 'position').all()

    # Получаем доступные фильтры
    filials = Filial.objects.all()
    positions = Position.objects.all()

    # Получаем параметры фильтрации из GET запроса
    selected_filial = request.GET.get('filial')
    selected_position = request.GET.get('position')
    selected_smus = request.GET.get('smus')
    sort_by = request.GET.get('sort', '')
    group_by = request.GET.get('group', '')

    # Применяем фильтры
    if selected_filial:
        employees = employees.filter(filial_id=selected_filial)

    if selected_position:
        employees = employees.filter(position_id=selected_position)

    if selected_smus:
        smus_bool = selected_smus.lower() == 'true'
        employees = employees.filter(is_smus=smus_bool)

    # Применяем сортировку
    if sort_by:
        if sort_by == 'name':
            # Сортировка по ФИО (фамилия + имя)
            employees = employees.order_by('user__last_name', 'user__first_name')
        elif sort_by == '-name':
            # Обратная сортировка по ФИО
            employees = employees.order_by('-user__last_name', '-user__first_name')
        elif sort_by == 'birth_date':
            employees = employees.order_by('birth_date')
        elif sort_by == '-birth_date':
            employees = employees.order_by('-birth_date')
        elif sort_by == 'position':
            employees = employees.order_by('position__name')
        elif sort_by == 'filial':
            employees = employees.order_by('filial__name')
    else:
        # Сортировка по умолчанию - по фамилии
        employees = employees.order_by('user__last_name')

    # Подготовка данных для шаблона
    context = {
        'employees': employees,
        'filials': filials,
        'positions': positions,
        'selected_filial': selected_filial,
        'selected_position': selected_position,
        'selected_smus': selected_smus,
        'sort_by': sort_by,
        'group_by': group_by,
    }

    # Добавляем имена для отображения в статистике
    if selected_filial:
        filial_obj = Filial.objects.filter(id=selected_filial).first()
        context['selected_filial_name'] = filial_obj.name if filial_obj else ''

    if selected_position:
        position_obj = Position.objects.filter(id=selected_position).first()
        context['selected_position_name'] = position_obj.name if position_obj else ''

    # Группировка сотрудников
    if group_by:
        grouped = {}
        for employee in employees:
            if group_by == 'filial':
                key = employee.filial.name if employee.filial else 'Не указан'
            elif group_by == 'position':
                key = employee.position.name if employee.position else 'Не указана'
            elif group_by == 'smus':
                key = "Члены СМУС" if employee.is_smus else "Не члены СМУС"

            if key not in grouped:
                grouped[key] = []
            grouped[key].append(employee)

        # Сортируем группы для красивого отображения
        if group_by == 'filial':
            grouped = dict(sorted(grouped.items(), key=lambda x: x[0]))
        elif group_by == 'position':
            grouped = dict(sorted(grouped.items(), key=lambda x: x[0]))
        elif group_by == 'smus':
            # Сначала члены СМУС, потом остальные
            sorted_groups = {}
            if "Члены СМУС" in grouped:
                sorted_groups["Члены СМУС"] = grouped["Члены СМУС"]
            if "Не члены СМУС" in grouped:
                sorted_groups["Не члены СМУС"] = grouped["Не члены СМУС"]
            grouped = sorted_groups

        context['grouped_employees'] = grouped

    return render(request, 'sotrudniki.html', context)

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

# Generic views для CRUD Employee
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    ordering = ['user__last_name', 'user__first_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        filial = self.request.GET.get('filial')
        if filial:
            queryset = queryset.filter(filial__name__icontains=filial)
        return queryset

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'



class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee  # Модель для Employee, но форма создаст и User
    form_class = EmployeeCreationForm  # Используем форму для создания User + Employee
    template_name = 'employees/employee_form.html'  # Шаблон формы
    success_url = reverse_lazy('sotrudniki')  # URL для перенаправления после успеха (список сотрудников)


class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('sotrudniki')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
import os


def export_rating_excel(request):
    try:
        # Получаем всех сотрудников
        employees = Employee.objects.all()

        # Создаем список данных для Excel
        data = []

        for employee in employees:
            # Рассчитываем количество мероприятий и баллы
            participations = Participation.objects.filter(employee=employee)
            smus_ratings = SMUSRating.objects.filter(smus__employee=employee)

            # Количество мероприятий
            kolichestvo_meropriyatiy = participations.count()

            # Считаем баллы за участие в мероприятиях
            event_points = sum([p.get_points() for p in participations])

            # Считаем баллы от СМУС (если есть)
            smus_points = sum([rating.score for rating in smus_ratings])

            # Итоговый балл
            itogovy_ball = event_points + Decimal(str(smus_points))

            # Определяем статус
            if itogovy_ball >= Decimal('5'):
                status = 'Лидер'
            elif itogovy_ball >= Decimal('3'):
                status = 'Активный'
            else:
                status = 'Участник'

            # Проверяем, является ли сотрудник членом СМУС
            is_smus_member = SMUS.objects.filter(employee=employee).exists()
            smus_info = "Да" if is_smus_member else "Нет"

            data.append({
                'ФИО': employee.user.get_full_name(),
                'Филиал': employee.filial.name if employee.filial else 'Не указан',
                'Должность': employee.position.name if employee.position else 'Не указана',
                'Внутренний телефон': employee.internal_phone,
                'Член СМУС': smus_info,
                'Количество мероприятий': kolichestvo_meropriyatiy,
                'Баллы за мероприятия': float(event_points),
                'Баллы от СМУС': float(smus_points),
                'Итоговый балл': float(itogovy_ball),
                'Статус': status
            })

        # Сортируем по итоговому баллу (по убыванию)
        data.sort(key=lambda x: x['Итоговый балл'], reverse=True)

        # Добавляем место
        for i, item in enumerate(data, 1):
            item['Место'] = i

        # Создаем DataFrame
        df = pd.DataFrame(data)

        # Переупорядочиваем колонки
        columns_order = ['Место', 'ФИО', 'Филиал', 'Должность', 'Внутренний телефон',
                         'Член СМУС', 'Количество мероприятий', 'Баллы за мероприятия',
                         'Баллы от СМУС', 'Итоговый балл', 'Статус']
        df = df[columns_order]

        # Создаем ответ
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Формируем имя файла с текущей датой
        filename = f"рейтинг_сотрудников_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Записываем DataFrame в Excel
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Рейтинг')

            # Автонастройка ширины колонок
            worksheet = writer.sheets['Рейтинг']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        return response

    except Exception as e:
        # Если произошла ошибка, редиректим на страницу рейтинга
        print(f"Ошибка при экспорте Excel: {e}")
        return redirect('reiting')

class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('sotrudniki')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


from django.views.decorators.csrf import csrf_exempt # Временно, см. примечание ниже

# Вместо csrf_exempt лучше использовать @ensure_csrf_cookie + стандартный CSRF
# Для простоты примера используем require_POST
@require_POST
def save_user_setting(request):
    """
    Сохраняет настройки темы или доступности в сессии пользователя.
    """
    try:
        # Проверяем, что запрос отправлен в формате JSON
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Неверный формат JSON"}, status=400)

    setting_key = data.get('key')
    setting_value = data.get('value')

    if setting_key in ['theme', 'accessible']:
        # Ключи 'theme' и 'accessible' разрешены
        # Сохраняем значение в сессии Django
        request.session[setting_key] = setting_value
        return JsonResponse({"status": "success", "key": setting_key, "value": setting_value})
    else:
        return JsonResponse({"status": "error", "message": "Недопустимый ключ настройки"}, status=400)


@require_POST
@never_cache
def set_language(request):
    lang_code = request.POST.get('language', settings.LANGUAGE_CODE)

    # Проверяем, что язык поддерживается
    if lang_code in dict(settings.LANGUAGES).keys():
        # Устанавливаем язык в сессии
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code

        # Устанавливаем язык в куках для JavaScript
        response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )
        return response

    # Если язык не поддерживается, возвращаем на предыдущую страницу
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))