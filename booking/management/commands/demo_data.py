"""
Management-Command: Demo-Buchungen anlegen oder löschen.

    python manage.py demo_data          # Demo-Daten anlegen
    python manage.py demo_data --delete # Demo-Daten wieder entfernen
"""

from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from booking.models import Booking, BookingSettings

# Alle Demo-Buchungen tragen dieses Kennzeichen in admin_note – so können
# sie jederzeit sauber und vollständig wieder entfernt werden.
DEMO_MARKER = '[DEMO]'

DEMO_BOOKINGS = [
    {
        'contact_name':  'FC Westfalia Jugend (U15)',
        'contact_email': 'demo1@example.com',
        'contact_phone': '01234 56789',
        'purpose':       'Saisonabschlussfeier Jugend',
        'notes':         'Ca. 30 Personen, Getränke selbst mitgebracht.',
        'offset_days':   16,
        'start_time':    time(14, 0),
        'end_time':      time(20, 0),
        'status':        Booking.STATUS_CONFIRMED,
        'admin_note':    f'{DEMO_MARKER} Testbuchung – bitte vor Live-Betrieb löschen.',
    },
    {
        'contact_name':  'Tennisabteilung Westfalia',
        'contact_email': 'demo2@example.com',
        'contact_phone': '09876 54321',
        'purpose':       'Jahreshauptversammlung',
        'notes':         '',
        'offset_days':   23,
        'start_time':    time(19, 0),
        'end_time':      time(22, 0),
        'status':        Booking.STATUS_CONFIRMED,
        'admin_note':    f'{DEMO_MARKER} Testbuchung – bitte vor Live-Betrieb löschen.',
    },
    {
        'contact_name':  'Familie Müller',
        'contact_email': 'demo3@example.com',
        'contact_phone': '',
        'purpose':       'Geburtstagsfeier (50. Geburtstag)',
        'notes':         'Bitte Bestuhlung für 40 Personen.',
        'offset_days':   30,
        'start_time':    time(15, 0),
        'end_time':      time(23, 0),
        'status':        Booking.STATUS_CONFIRMED,
        'admin_note':    f'{DEMO_MARKER} Testbuchung – bitte vor Live-Betrieb löschen.',
    },
    {
        'contact_name':  'Schützenverein Osterwick',
        'contact_email': 'demo4@example.com',
        'contact_phone': '02241 111222',
        'purpose':       'Vereinstreffen mit Abendessen',
        'notes':         '',
        'offset_days':   38,
        'start_time':    time(18, 0),
        'end_time':      time(23, 0),
        'status':        Booking.STATUS_CONFIRMED,
        'admin_note':    f'{DEMO_MARKER} Testbuchung – bitte vor Live-Betrieb löschen.',
    },
    {
        'contact_name':  'Max Testmann',
        'contact_email': 'demo5@example.com',
        'contact_phone': '0171 9998877',
        'purpose':       'Kindergeburtstag',
        'notes':         'Torte wird selbst mitgebracht.',
        'offset_days':   44,
        'start_time':    time(13, 0),
        'end_time':      time(18, 0),
        'status':        Booking.STATUS_CANCELLED,
        'admin_note':    f'{DEMO_MARKER} Storniertes Demo – zeigt stornierte Buchung in der Liste.',
    },
]


class Command(BaseCommand):
    help = 'Demo-Buchungen anlegen (Standard) oder löschen (--delete)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Alle vorhandenen Demo-Buchungen löschen',
        )

    def handle(self, *args, **options):
        if options['delete']:
            self._delete_demo_data()
        else:
            self._create_demo_data()

    def _delete_demo_data(self):
        qs = Booking.objects.filter(admin_note__startswith=DEMO_MARKER)
        count = qs.count()
        qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f'{count} Demo-Buchung(en) gelöscht.'
        ))

    def _create_demo_data(self):
        today = date.today()
        cfg = BookingSettings.get()
        min_offset = cfg.min_advance_days

        created = 0
        for data in DEMO_BOOKINGS:
            booking_date = today + timedelta(days=max(data['offset_days'], min_offset))
            # Überspringe, falls an diesem Tag schon eine Demo-Buchung liegt
            if Booking.objects.filter(
                date=booking_date,
                admin_note__startswith=DEMO_MARKER
            ).exists():
                self.stdout.write(
                    f'  Übersprungen (Datum belegt): {booking_date}'
                )
                continue

            Booking.objects.create(
                contact_name=data['contact_name'],
                contact_email=data['contact_email'],
                contact_phone=data['contact_phone'],
                purpose=data['purpose'],
                notes=data['notes'],
                date=booking_date,
                start_time=data['start_time'],
                end_time=data['end_time'],
                status=data['status'],
                admin_note=data['admin_note'],
            )
            self.stdout.write(f'  + {booking_date} {data["start_time"]}–{data["end_time"]} | {data["contact_name"]}')
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{created} Demo-Buchung(en) angelegt. '
            f'Löschen mit: python manage.py demo_data --delete'
        ))
