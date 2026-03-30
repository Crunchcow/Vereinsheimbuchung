import json
import uuid
from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

from .models import Booking, BookingSettings, BlockedDate
from .forms import BookingForm, BookingStatusForm
from .permissions import is_verwaltung_or_admin, is_admin


# ── Hilfs-Decorator ──────────────────────────────────────────────────────────

def verwaltung_required(view_func):
    """Zugriff nur für Verwaltung und Admin."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_verwaltung_or_admin(request.user):
            messages.error(request, 'Keine Berechtigung.')
            return redirect('calendar')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Auth ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('calendar')
    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'calendar'))
        error = 'Benutzername oder Passwort falsch.'
    return render(request, 'booking/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Kalender (Startseite) ─────────────────────────────────────────────────────

def calendar_view(request):
    cfg = BookingSettings.get()
    today = date.today()
    min_date = today + timedelta(days=cfg.min_advance_days)
    max_date = today + timedelta(days=cfg.max_booking_months * 30)
    blocked_dates = list(
        BlockedDate.objects.values_list('date', flat=True)
    )
    blocked_dates_iso = [d.isoformat() for d in blocked_dates]
    return render(request, 'booking/calendar.html', {
        'min_date': min_date,
        'max_date': max_date,
        'settings': cfg,
        'blocked_dates_json': json.dumps(blocked_dates_iso),
    })


# ── API: Buchungen für FullCalendar ───────────────────────────────────────────

@require_GET
def api_events(request):
    """Liefert Events als JSON für FullCalendar.
    User sieht nur 'Belegt', keine Details.
    Verwaltung/Admin sieht Name + Anlass."""
    start = request.GET.get('start', '')
    end   = request.GET.get('end', '')

    qs = Booking.objects.filter(
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]
    )
    if start:
        qs = qs.filter(date__gte=start[:10])
    if end:
        qs = qs.filter(date__lte=end[:10])

    show_details = is_verwaltung_or_admin(request.user)
    blocked = BlockedDate.objects.filter(date__gte=start[:10], date__lte=end[:10]) if start and end else BlockedDate.objects.all()

    events = []

    # Geblockte Tage
    for bd in blocked:
        events.append({
            'id': f'blocked_{bd.pk}',
            'title': f'Gesperrt: {bd.reason}' if bd.reason else 'Gesperrt',
            'start': bd.date.isoformat(),
            'allDay': True,
            'color': '#6c757d',
            'display': 'background',
        })

    for b in qs:
        color = '#c00000' if b.status == Booking.STATUS_CONFIRMED else '#e07070'
        if show_details:
            title = f'{b.contact_name} – {b.purpose}'
            url = f'/buchungen/{b.pk}/'
        else:
            von = b.start_time.strftime('%H:%M')
            bis = b.end_time.strftime('%H:%M')
            title = f'Belegt {von}–{bis} Uhr'
            url = None
        event = {
            'id': b.pk,
            'title': title,
            'start': f'{b.date.isoformat()}T{b.start_time.strftime("%H:%M:%S")}',
            'end':   f'{b.date.isoformat()}T{b.end_time.strftime("%H:%M:%S")}',
            'color': color,
            'extendedProps': {
                'status': b.status,
                'status_label': b.status_label,
            },
        }
        if url:
            event['url'] = url
        events.append(event)

    return JsonResponse(events, safe=False)


# ── Buchung erstellen ─────────────────────────────────────────────────────────

def booking_create(request):
    cfg = BookingSettings.get()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.created_by = request.user
            # Termin ist frei (von der Form bereits geprüft) → direkt bestätigen
            booking.status = Booking.STATUS_CONFIRMED
            booking.save()

            datum = booking.date.strftime('%d.%m.%Y')
            von   = booking.start_time.strftime('%H:%M')
            bis   = booking.end_time.strftime('%H:%M')

            cancel_url = request.build_absolute_uri(
                reverse('booking_cancel', args=[booking.cancellation_token])
            )
            ics_content = _generate_ics(booking)

            # 1) Bestätigungs-E-Mail an den Buchenden (mit .ics-Anhang + Stornierungslink)
            try:
                email = EmailMessage(
                    subject='Buchungsbestätigung – Sportheim Westfalia Osterwick',
                    body=(
                        f'Hallo {booking.contact_name},\n\n'
                        f'Deine Buchung des Sportheims wurde bestätigt:\n\n'
                        f'  Datum:  {datum}\n'
                        f'  Zeit:   {von} – {bis} Uhr\n'
                        f'  Anlass: {booking.purpose}\n\n'
                        f'Den Termin kannst du mit der angehängten .ics-Datei\n'
                        f'direkt in deinen Kalender (Outlook, Google, Apple) übernehmen.\n\n'
                        f'Falls du den Termin absagen möchtest, kannst du ihn hier stornieren:\n'
                        f'{cancel_url}\n\n'
                        f'Bei Rückfragen wende dich bitte an sportheim@westfalia-osterwick.de.\n\n'
                        f'Mit freundlichen Grüßen\n'
                        f'Westfalia Osterwick e. V.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[booking.contact_email],
                )
                email.attach('termin.ics', ics_content, 'text/calendar; charset=utf-8')
                email.send(fail_silently=True)
            except Exception:
                pass

            # 2) Benachrichtigung an das Sportheim-Team
            notify_email = getattr(settings, 'NOTIFY_EMAIL', cfg.contact_email)
            try:
                EmailMessage(
                    subject=f'Neue Buchung: {booking.contact_name} ({datum})',
                    body=(
                        f'Eine neue Buchung wurde eingetragen:\n\n'
                        f'  Name:    {booking.contact_name}\n'
                        f'  Anlass:  {booking.purpose}\n'
                        f'  Datum:   {datum}\n'
                        f'  Zeit:    {von} – {bis} Uhr\n'
                        f'  E-Mail:  {booking.contact_email}\n'
                        f'  Telefon: {booking.contact_phone or "–"}\n'
                        f'  Notiz:   {booking.notes or "–"}\n\n'
                        f'Status: {booking.status_label}\n'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[notify_email],
                ).send(fail_silently=True)
            except Exception:
                pass

            messages.success(request, 'Deine Buchung wurde bestätigt! Eine Bestätigungs-E-Mail mit Kalender-Anhang wurde an dich gesendet.')
            return redirect('booking_success', pk=booking.pk)
    else:
        # Datum aus GET-Parameter vorbelegen (vom Kalender-Klick)
        initial = {}
        if d := request.GET.get('date'):
            # Gesperrte Tage dürfen nicht gebucht werden
            try:
                from datetime import date as date_type
                clicked = date_type.fromisoformat(d)
                if BlockedDate.objects.filter(date=clicked).exists():
                    messages.error(request, 'Dieser Tag ist gesperrt und kann nicht gebucht werden.')
                    return redirect('calendar')
            except ValueError:
                pass
            initial['date'] = d
        form = BookingForm(initial=initial)

    return render(request, 'booking/booking_form.html', {
        'form': form,
        'settings': cfg,
        'min_date': date.today() + timedelta(days=cfg.min_advance_days),
        'blocked_dates_json': json.dumps([d.isoformat() for d in BlockedDate.objects.values_list('date', flat=True)]),
    })


def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'booking/booking_success.html', {'booking': booking})


# ── Buchungsliste (Verwaltung / Admin) ────────────────────────────────────────

@verwaltung_required
def booking_list(request):
    status_filter = request.GET.get('status', '')
    qs = Booking.objects.select_related('created_by').order_by('-created_at', '-date')
    if status_filter:
        qs = qs.filter(status=status_filter)
    pending_count = Booking.objects.filter(status=Booking.STATUS_PENDING).count()
    return render(request, 'booking/booking_list.html', {
        'bookings': qs,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
        'pending_count': pending_count,
    })


@verwaltung_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    form = BookingStatusForm(instance=booking)

    if request.method == 'POST' and is_verwaltung_or_admin(request.user):
        old_status = booking.status
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()

            # Nur bei Stornierung eine E-Mail senden – alle anderen Buchungen
            # werden automatisch bestätigt, d. h. confirmed/rejected kommen
            # in der Praxis nicht vor.
            if old_status != Booking.STATUS_CANCELLED and booking.status == Booking.STATUS_CANCELLED:
                datum = booking.date.strftime('%d.%m.%Y')
                von   = booking.start_time.strftime('%H:%M')
                bis   = booking.end_time.strftime('%H:%M')

                # Stornierungsmail an den Buchenden
                try:
                    EmailMessage(
                        subject='Deine Buchung des Sportheims wurde storniert',
                        body=(
                            f'Hallo {booking.contact_name},\n\n'
                            f'deine Buchung des Sportheims wurde von der Verwaltung storniert:\n\n'
                            f'  Datum:  {datum}\n'
                            f'  Zeit:   {von} – {bis} Uhr\n'
                            f'  Anlass: {booking.purpose}\n\n'
                            f'Falls du Fragen hast oder einen neuen Termin buchen möchtest,\n'
                            f'melde dich gerne unter sportheim@westfalia-osterwick.de\n'
                            f'oder buche direkt unter https://sportheim.westfalia-osterwick.de/.\n\n'
                            f'Mit freundlichen Grüßen\n'
                            f'Westfalia Osterwick e. V.'
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[booking.contact_email],
                    ).send(fail_silently=True)
                except Exception:
                    pass

            messages.success(request, f'Status auf „{booking.status_label}" gesetzt.')
            return redirect('booking_detail', pk=pk)

    return render(request, 'booking/booking_detail.html', {
        'booking': booking,
        'form': form,
    })


# ── Impressum & Datenschutz ───────────────────────────────────────────────────

def impressum(request):
    return render(request, 'booking/impressum.html')


def datenschutz(request):
    return render(request, 'booking/datenschutz.html')


# ── Hilfsfunktion: iCalendar (.ics) ──────────────────────────────────────────

def _generate_ics(booking):
    """Erzeugt iCalendar-Inhalt für eine Buchung (kein externes Paket nötig)."""
    start_dt = datetime.combine(booking.date, booking.start_time)
    end_dt   = datetime.combine(booking.date, booking.end_time)
    now_utc  = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    summary  = f'Sportheim Westfalia Osterwick – {booking.purpose}'
    return (
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//Westfalia Osterwick//Sportheimbuchung//DE\r\n'
        'METHOD:PUBLISH\r\n'
        'BEGIN:VEVENT\r\n'
        f'UID:booking-{booking.pk}@westfalia-osterwick.de\r\n'
        f'DTSTAMP:{now_utc}\r\n'
        f'DTSTART:{start_dt.strftime("%Y%m%dT%H%M%S")}\r\n'
        f'DTEND:{end_dt.strftime("%Y%m%dT%H%M%S")}\r\n'
        f'SUMMARY:{summary}\r\n'
        'LOCATION:Sportheim Westfalia Osterwick\\, Osterwick\r\n'
        f'DESCRIPTION:Gebucht von: {booking.contact_name}\r\n'
        'END:VEVENT\r\n'
        'END:VCALENDAR\r\n'
    )


# ── .ics Download ─────────────────────────────────────────────────────────────

@login_required
def booking_ics(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.created_by != request.user and not is_verwaltung_or_admin(request.user):
        messages.error(request, 'Keine Berechtigung.')
        return redirect('calendar')
    ics = _generate_ics(booking)
    response = HttpResponse(ics, content_type='text/calendar; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="sportheim-{booking.date.isoformat()}.ics"'
    return response


# ── API: Verfügbarkeits-Check (Live-Validierung im Formular) ──────────────────

@require_GET
def api_check_availability(request):
    """Prüft ob ein Zeitfenster buchbar ist (AJAX, für Live-Validierung)."""
    from datetime import date as date_type, time as time_type
    date_str  = request.GET.get('date', '')
    start_str = request.GET.get('start', '')
    end_str   = request.GET.get('end', '')

    if not (date_str and start_str and end_str):
        return JsonResponse({'available': True, 'conflicts': []})

    try:
        booking_date = date_type.fromisoformat(date_str)
        start_time   = time_type.fromisoformat(start_str)
        end_time     = time_type.fromisoformat(end_str)
    except ValueError:
        return JsonResponse({'available': True, 'conflicts': []})

    if start_time >= end_time:
        return JsonResponse({
            'available': False,
            'conflicts': [],
            'error': 'Endzeit muss nach der Startzeit liegen.',
        })

    # Gesperrter Tag?
    blocked = BlockedDate.objects.filter(date=booking_date).first()
    if blocked:
        reason = blocked.reason or 'Dieser Tag ist vom Admin gesperrt.'
        return JsonResponse({
            'available': False,
            'conflicts': [],
            'blocked': True,
            'blocked_reason': reason,
        })

    conflicts = []
    for b in Booking.objects.filter(
        date=booking_date,
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
    ):
        if b.start_time < end_time and b.end_time > start_time:
            conflicts.append({
                'start': b.start_time.strftime('%H:%M'),
                'end':   b.end_time.strftime('%H:%M'),
            })

    return JsonResponse({'available': len(conflicts) == 0, 'conflicts': conflicts})


# ── Stornierung (token-basiert, kein Login nötig) ─────────────────────────────

def booking_cancel(request, token):
    booking = get_object_or_404(Booking, cancellation_token=token)

    # Bereits storniert oder abgelehnt?
    if booking.status in [Booking.STATUS_CANCELLED, Booking.STATUS_REJECTED]:
        return render(request, 'booking/booking_cancel.html', {
            'booking': booking, 'already_done': True,
        })

    # Termin liegt in der Vergangenheit?
    if booking.date < date.today():
        return render(request, 'booking/booking_cancel.html', {
            'booking': booking, 'past': True,
        })

    if request.method == 'POST':
        booking.status = Booking.STATUS_CANCELLED
        booking.admin_note = (booking.admin_note + '\n' if booking.admin_note else '') + 'Storniert vom Buchenden.'
        booking.save()

        datum = booking.date.strftime('%d.%m.%Y')
        von   = booking.start_time.strftime('%H:%M')
        bis   = booking.end_time.strftime('%H:%M')

        # Team informieren
        notify_email = getattr(settings, 'NOTIFY_EMAIL', '')
        if notify_email:
            try:
                EmailMessage(
                    subject=f'Buchung storniert: {booking.contact_name} ({datum})',
                    body=(
                        f'Die folgende Buchung wurde vom Buchenden storniert:\n\n'
                        f'  Name:   {booking.contact_name}\n'
                        f'  Anlass: {booking.purpose}\n'
                        f'  Datum:  {datum}\n'
                        f'  Zeit:   {von} – {bis} Uhr\n'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[notify_email],
                ).send(fail_silently=True)
            except Exception:
                pass

        return render(request, 'booking/booking_cancel.html', {
            'booking': booking, 'cancelled': True,
        })

    return render(request, 'booking/booking_cancel.html', {'booking': booking})


def datenschutz(request):
    return render(request, 'booking/datenschutz.html')

