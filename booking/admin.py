from django.contrib import admin
from .models import Booking, BookingSettings, BlockedDate


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'contact_name', 'purpose', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('contact_name', 'contact_email', 'purpose')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    fieldsets = (
        ('Termin', {'fields': ('date', 'start_time', 'end_time')}),
        ('Kontakt', {'fields': ('contact_name', 'contact_email', 'contact_phone', 'purpose', 'notes')}),
        ('Verwaltung', {'fields': ('status', 'admin_note', 'created_by', 'created_at', 'updated_at')}),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BookingSettings)
class BookingSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not BookingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason')
    ordering = ('date',)

