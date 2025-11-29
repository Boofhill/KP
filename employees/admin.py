from django.contrib import admin
from .models import Filial, Position, Employee, SMUS, Event, Participation, SMUSRating

@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    search_fields = ('name',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'filial', 'position', 'internal_phone', 'is_smus')
    list_filter = ('filial', 'position', 'is_smus')
    search_fields = ('user__first_name', 'user__last_name', 'internal_phone')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'ФИО'

@admin.register(SMUS)
class SMUSAdmin(admin.ModelAdmin):
    list_display = ('employee', 'position')
    list_filter = ('position',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'direction', 'creator', 'year')
    list_filter = ('direction', 'year')
    search_fields = ('name',)

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'event', 'role')
    list_filter = ('event', 'role')

@admin.register(SMUSRating)
class SMUSRatingAdmin(admin.ModelAdmin):
    list_display = ('smus', 'event', 'score')
    list_filter = ('event',)