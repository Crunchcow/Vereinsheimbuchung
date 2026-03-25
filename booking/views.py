import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.mail import send_mail
from django.conf import settings

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

@login_required
def calendar_view(request):
    cfg = BookingSettings.get()
    today = date.today()
    min_date = today + timedelta(days=cfg.min_advance_days)
    max_date = today + timedelta(days=cfg.max_booking_months * 30)
    return render(request, 'booking/calendar.html', {
        'min_date': min_date.isoformat(),
        'max_date': max_date.isoformat(),
        'settings': cfg,
    })


# ── API: Buchungen für FullCalendar ───────────────────────────────────────────

@login_required
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
            title = 'Belegt'
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

@login_required
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

            # 1) Bestätigungs-E-Mail an den Buchenden
            try:
                send_mail(
                    subject='Buchungsbestätigung – Sportheim Westfalia Osterwick',
                    message=(
                        f'Hallo {booking.contact_name},\n\n'
                        f'Deine Buchung des Sportheims wurde bestätigt:\n\n'
                        f'  Datum: {datum}\n'
                        f'  Zeit:  {von} – {bis} Uhr\n'
                        f'  Anlass: {booking.purpose}\n\n'
                        f'Bei Fragen wende dich bitte an sportheim@westfalia-osterwick.de.\n\n'
                        f'Mit freundlichen Grüßen\n'
                        f'Westfalia Osterwick e. V.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.contact_email],
                    fail_silently=True,
                )
            except Exception:
                pass

            # 2) Benachrichtigung an das Sportheim-Team
            notify_email = getattr(settings, 'NOTIFY_EMAIL', cfg.contact_email)
            try:
                send_mail(
                    subject=f'Neue Buchung: {booking.contact_name} ({datum})',
                    message=(
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
                    recipient_list=[notify_email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, 'Deine Buchung wurde bestätigt! Eine Bestätigungs-E-Mail wurde an dich gesendet.')
            return redirect('booking_success', pk=booking.pk)
    else:
        # Datum aus GET-Parameter vorbelegen (vom Kalender-Klick)
        initial = {}
        if d := request.GET.get('date'):
            initial['date'] = d
        form = BookingForm(initial=initial)

    return render(request, 'booking/booking_form.html', {'form': form, 'settings': cfg})


@login_required
def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    # Nur eigene Buchungen oder Verwaltung/Admin
    if booking.created_by != request.user and not is_verwaltung_or_admin(request.user):
        messages.error(request, 'Keine Berechtigung.')
        return redirect('calendar')
    return render(request, 'booking/booking_success.html', {'booking': booking})


# ── Buchungsliste (Verwaltung / Admin) ────────────────────────────────────────

@verwaltung_required
def booking_list(request):
    status_filter = request.GET.get('status', '')
    qs = Booking.objects.select_related('created_by').order_by('-date', '-start_time')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'booking/booking_list.html', {
        'bookings': qs,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
    })


@verwaltung_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    form = BookingStatusForm(instance=booking)

    if request.method == 'POST' and is_verwaltung_or_admin(request.user):
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status aktualisiert.')
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

