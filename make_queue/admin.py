from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from util.admin_utils import TextFieldOverrideMixin
from web.multilingual.admin import MultiLingualFieldAdmin
from .models.course import Printer3DCourse
from .models.machine import Machine, MachineType, MachineUsageRule
from .models.reservation import Quota, Reservation, ReservationRule


class MachineTypeAdmin(MultiLingualFieldAdmin):
    list_display = ('name', 'usage_requirement', 'has_stream', 'get_num_machines', 'priority')
    list_filter = ('usage_requirement', 'has_stream')
    search_fields = ('name', 'cannot_use_text')
    list_editable = ('priority',)
    ordering = ('priority',)

    @admin.display(
        ordering='machines__count',
        description=_("machines"),
    )
    def get_num_machines(self, machine_type: MachineType):
        return machine_type.machines__count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(Count('machines'))  # facilitates querying `machines__count`


class MachineAdmin(TextFieldOverrideMixin, admin.ModelAdmin):
    list_display = ('name', 'machine_model', 'machine_type', 'get_location', 'status', 'priority', 'get_stream_name', 'last_modified')
    list_filter = ('machine_type', 'machine_model', 'location', 'status')
    search_fields = ('name', 'stream_name', 'machine_model', 'machine_type__name', 'location', 'location_url')
    list_editable = ('status', 'priority')
    list_select_related = ('machine_type',)

    readonly_fields = ('last_modified',)

    @admin.display(
        ordering='location',
        description=_("location"),
    )
    def get_location(self, machine: Machine):
        return format_html('<a href="{}" target="_blank">{}</a>', machine.location_url, machine.location)

    @admin.display(
        ordering='stream_name',
        description=_("stream name"),
    )
    def get_stream_name(self, machine: Machine):
        return machine.stream_name or None

    def get_queryset(self, request):
        return super().get_queryset(request).default_order_by()


class MachineUsageRuleAdmin(MultiLingualFieldAdmin, SimpleHistoryAdmin):
    list_display = ('machine_type', 'last_modified')
    list_select_related = ('machine_type',)

    readonly_fields = ('last_modified',)


class ReservationAdmin(TextFieldOverrideMixin, admin.ModelAdmin):
    pass


class ReservationRuleAdmin(admin.ModelAdmin):
    list_display = (
        'machine_type',
        'start_time', 'end_time',
        'days_changed', 'start_days',
        'max_hours', 'max_inside_border_crossed',
        'last_modified',
    )
    list_select_related = ('machine_type',)

    readonly_fields = ('last_modified',)


class Printer3DCourseAdmin(admin.ModelAdmin):
    list_display = ('username', 'user', 'name', 'date', 'status', 'advanced_course', 'last_modified')
    list_filter = ('status', 'advanced_course')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'username', 'name',
        'user__card_number', '_card_number',
    )
    list_editable = ('status', 'advanced_course')
    ordering = ('date', 'username')
    list_select_related = ('user',)

    readonly_fields = ('last_modified',)


admin.site.register(MachineType, MachineTypeAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineUsageRule, MachineUsageRuleAdmin)
admin.site.register(Quota)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ReservationRule, ReservationRuleAdmin)

admin.site.register(Printer3DCourse, Printer3DCourseAdmin)
