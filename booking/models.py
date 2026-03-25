from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BookingSettings(models.Model):
    """Globale Einstellungen – immer nur 1 Eintrag (Singleton)."""
    min_advance_days = models.PositiveIntegerField(
        default=14,
        verbose_name='Mindestvorlauf (Tage)',
        help_text='Wie viele Tage im Voraus muss gebucht werden?'
    )
    max_booking_months = models.PositiveIntegerField(
        default=6,
        verbose_name='Maximaler Buchungszeitraum (Monate)',
        help_text='Wie weit in die Zukunft darf gebucht werden?'
    )
    contact_name = models.CharField(
        max_length=200, default='Peter Fedders / Eike Nonhoff',
        verbose_name='Ansprechpartner'
    )
    contact_email = models.EmailField(
        default='sportheim@westfalia-osterwick.de',
        verbose_name='Kontakt-E-Mail'
    )

    class Meta:
        verbose_name = 'Einstellungen'
        verbose_name_plural = 'Einstellungen'

    def __str__(self):
        return 'Buchungseinstellungen'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BlockedDate(models.Model):
    """Gesperrte Einzeltage (Feiertage, Veranstaltungen etc.)."""
    date = models.DateField(verbose_name='Datum', unique=True)
    reason = models.CharField(max_length=200, verbose_name='Grund', blank=True)

    class Meta:
        verbose_name = 'Gesperrter Tag'
        verbose_name_plural = 'Gesperrte Tage'
        ordering = ['date']

    def __str__(self):
        return f'{self.date.strftime("%d.%m.%Y")} – {self.reason or "gesperrt"}'


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING,   'Ausstehend'),
        (STATUS_CONFIRMED, 'Bestätigt'),
        (STATUS_REJECTED,  'Abgelehnt'),
    ]

    # Antragsteller
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bookings', verbose_name='Erstellt von'
    )

    # Kontaktdaten (werden auch ohne Account ausgefüllt)
    contact_name = models.CharField(max_length=200, verbose_name='Name / Gruppe')
    contact_email = models.EmailField(verbose_name='E-Mail')
    contact_phone = models.CharField(max_length=50, blank=True, verbose_name='Telefon')
    purpose = models.CharField(max_length=300, verbose_name='Anlass / Zweck')
    notes = models.TextField(blank=True, verbose_name='Bemerkungen')

    # Termin
    date = models.DateField(verbose_name='Datum')
    start_time = models.TimeField(verbose_name='Von')
    end_time = models.TimeField(verbose_name='Bis')

    # Status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default=STATUS_PENDING, verbose_name='Status'
    )
    admin_note = models.TextField(
        blank=True, verbose_name='Interne Notiz (Admin)',
        help_text='Nur für Admin und Verwaltung sichtbar'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Buchung'
        verbose_name_plural = 'Buchungen'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.date.strftime("%d.%m.%Y")} {self.start_time.strftime("%H:%M")}–{self.end_time.strftime("%H:%M")} | {self.contact_name}'

    def overlaps_with(self, other_date, other_start, other_end):
        """Prüft ob diese Buchung zeitlich überlappt."""
        if self.date != other_date:
            return False
        return self.start_time < other_end and self.end_time > other_start

    @property
    def status_badge_class(self):
        return {
            self.STATUS_PENDING:   'warning',
            self.STATUS_CONFIRMED: 'success',
            self.STATUS_REJECTED:  'danger',
        }.get(self.status, 'secondary')

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

