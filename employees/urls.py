from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # Добавляем импорт

urlpatterns = [
                  # Основные маршруты
                  path('', views.glavnaya, name='glavnaya'),
                  path('sotrudniki/', views.sotrudniki, name='sotrudniki'),
                  path('meropriyatiya/', views.meropriyatiya, name='meropriyatiya'),
                  path('smus/', views.smus, name='smus'),
                  path('reiting/', views.reiting, name='reiting'),
                  path('meropriyatiya/<int:event_id>/ocenki/', views.ocenki_meropriyatiya, name='ocenki_meropriyatiya'),

                  path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
                  path('employees/new/', views.EmployeeCreateView.as_view(), name='employee_create'),
                  path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
                  path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
                  # Маршруты авторизации - ДОБАВЛЯЕМ ЭТО
                  path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
                  path('logout/', auth_views.LogoutView.as_view(next_page='glavnaya'), name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    path('i18n/', include('django.conf.urls.i18n')),
]


