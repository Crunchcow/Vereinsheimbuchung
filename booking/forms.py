from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, time, timedelta
from .models import Booking, BookingSettings, BlockedDate

BOOKING_START_MIN = time(8, 0)   # früheste Startzeit
BOOKING_END_MAX   = time(0, 0)   # späteste Endzeit (Mitternacht = 00:00 = nächster Tag)


class BookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Datum',
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'min': '08:00', 'max': '23:59'}),
        label='Von',
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'min': '08:01', 'max': '00:00'}),
        label='Bis',
    )

    class Meta:
        model = Booking
        fields = ['contact_name', 'contact_email', 'contact_phone', 'purpose', 'notes', 'date', 'start_time', 'end_time']
        widgets = {
            'contact_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose':       forms.TextInput(attrs={'class': 'form-control'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'contact_name':  'Name / Gruppe',
            'contact_email': 'E-Mail',
            'contact_phone': 'Telefon (optional)',
            'purpose':       'Anlass / Zweck',
            'notes':         'Bemerkungen (optional)',
        }

    def clean(self):
        cleaned = super().clean()
        booking_date = cleaned.get('date')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')

        if not (booking_date and start_time and end_time):
            return cleaned

        settings = BookingSettings.get()

        # Mindestvorlauf prüfen
        min_date = date.today() + timedelta(days=settings.min_advance_days)
        if booking_date < min_date:
            raise ValidationError(
                f'Buchungen müssen mindestens {settings.min_advance_days} Tage im Voraus erfolgen. '
                f'Frühestes Datum: {min_date.strftime("%d.%m.%Y")}'
            )

        # Maximaler Buchungszeitraum
        max_date = date.today() + timedelta(days=settings.max_booking_months * 30)
        if booking_date > max_date:
            raise ValidationError(
                f'Buchungen sind maximal {settings.max_booking_months} Monate im Voraus möglich.'
            )

        # Zeiten prüfen
        if end_time <= start_time:
            raise ValidationError('Die Endzeit muss nach der Startzeit liegen.')

        # Buchungsrahmen 08:00 – 24:00 Uhr
        if start_time < BOOKING_START_MIN:
            raise ValidationError('Die Startzeit muss ab 08:00 Uhr liegen.')
        # Endzeit 00:00 bedeutet Mitternacht (= Ende um 24:00), alles andere bis max 00:00 nächster Tag
        # Wir erlauben start >= 08:00 und end <= 23:59 ODER end == 00:00 (Mitternacht)
        if end_time != time(0, 0) and end_time > time(23, 59):
            raise ValidationError('Die Endzeit darf maximal 24:00 Uhr (00:00) sein.')

        # Gesperrte Tage
        if BlockedDate.objects.filter(date=booking_date).exists():
            raise ValidationError('Dieser Tag ist gesperrt. Bitte wähle ein anderes Datum.')

        # Überschneidungen
        existing = Booking.objects.filter(
            date=booking_date,
            status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]
        )
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)

        for b in existing:
            if b.start_time < end_time and b.end_time > start_time:
                raise ValidationError(
                    f'Der Zeitraum überschneidet sich mit einer bestehenden Buchung '
                    f'({b.start_time.strftime("%H:%M")}–{b.end_time.strftime("%H:%M")}).'
                )

        return cleaned


class BookingStatusForm(forms.ModelForm):
    """Für Admin/Verwaltung: Status und interne Notiz ändern."""
    class Meta:
        model = Booking
        fields = ['status', 'admin_note']
        widgets = {
            'status':     forms.Select(attrs={'class': 'form-select'}),
            'admin_note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
