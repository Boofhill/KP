from django.urls import path
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

                  # Маршруты авторизации - ДОБАВЛЯЕМ ЭТО
                  path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
                  path('logout/', auth_views.LogoutView.as_view(next_page='glavnaya'), name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)