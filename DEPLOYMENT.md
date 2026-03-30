# Vereinsheimbuchung – Deployment auf Hetzner

## Server-Infos

| | |
|---|---|
| **IP** | `89.167.0.28` |
| **Hostname** | `WestfaliaOsterwick` (Ubuntu 24.04) |
| **App-Pfad** | `/var/www/vereinsheimbuchung/` |
| **Domain** | `https://sportheim.westfalia-osterwick.de` |
| **Stack** | Nginx → Gunicorn (kein Docker) |
| **Gunicorn-Port** | `127.0.0.1:8002` |
| **Nginx-Config** | `/etc/nginx/sites-enabled/vereinsheimbuchung` |
| **Gunicorn PID** | Ermitteln mit: `pgrep -f 'gunicorn vereinsheimbuchung'` |

---

## Update deployen (nach jedem `git push`)

```bash
ssh root@89.167.0.28 'cd /var/www/vereinsheimbuchung && git pull origin main && PID=$(pgrep -f gunicorn | head -1) && kill -HUP $PID && echo "DONE, PID: $PID"'
```

> **Gunicorn komplett neu starten** (nach Kill oder Absturz):
> ```bash
> ssh root@89.167.0.28 'cd /var/www/vereinsheimbuchung && .venv/bin/gunicorn vereinsheimbuchung.wsgi:application --bind 127.0.0.1:8002 --workers 3 --daemon --log-file /var/log/nginx/gunicorn-vereinsheimbuchung.log'
> ```

### Was muss ich zusätzlich ausführen?

| Was geändert? | Befehle nötig |
|---|---|
| Nur Templates (`.html`) | `git pull` + `kill -HUP` |
| Python-Code (`views.py`, `models.py`, ...) | `git pull` + `kill -HUP` |
| Neue Migration (`models.py` mit neuen Feldern) | + `python manage.py migrate` |
| Neues Paket in `requirements.txt` | + `pip install -r requirements.txt` |
| Static Files (`static/`) | + `python manage.py collectstatic --noinput` |

> **Hinweis:** `git pull` allein reicht nie – Gunicorn cached Templates und Python-Code im Speicher (`DEBUG=False`). Immer `kill -HUP` ausführen.

---

## Vollständiges Update (alle Schritte)

```bash
ssh root@89.167.0.28
cd /var/www/vereinsheimbuchung
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt          # nur bei neuen Paketen
python manage.py migrate --noinput       # nur bei neuen Migrationen
python manage.py collectstatic --noinput # nur bei Static-Änderungen
kill -HUP $(pgrep -f 'gunicorn vereinsheimbuchung' | head -1)
```

---

## Nützliche Befehle auf dem Server

```bash
# Gunicorn-PID anzeigen
pgrep -f 'gunicorn vereinsheimbuchung'

# Gunicorn graceful reload (kein Downtime)
kill -HUP <PID>

# Gunicorn-Prozesse anzeigen
ps aux | grep gunicorn

# Django-Shell
cd /var/www/vereinsheimbuchung
source .venv/bin/activate
python manage.py shell

# Nginx-Config testen und neu laden
nginx -t && systemctl reload nginx

# Logs
journalctl -u nginx -f
tail -f /var/log/nginx/error.log
```

---

## Demo-Daten

```bash
# Demo-Buchungen anlegen (zum Testen)
python manage.py demo_data

# Demo-Buchungen wieder löschen (vor Live-Betrieb!)
python manage.py demo_data --delete
```

---

## Passwort eines Benutzers zurücksetzen

```bash
python manage.py changepassword <benutzername>
```

Benutzernamen abfragen:
```bash
python manage.py shell -c "from django.contrib.auth.models import User; print(list(User.objects.values_list('username', flat=True)))"
```

---

## Erstmalige Einrichtung (Referenz)

```bash
cd /var/www/vereinsheimbuchung
cp .env.example .env
nano .env   # SECRET_KEY, ALLOWED_HOSTS, MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET, MS_SENDER eintragen

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Gunicorn als Daemon starten:
```bash
gunicorn vereinsheimbuchung.wsgi:application --workers 3 --bind 127.0.0.1:8002 --daemon --chdir /var/www/vereinsheimbuchung
```

---

## Benutzer & Gruppen

| Benutzer | Rolle | Zugang |
|---|---|---|
| `Crunchcow` | Superuser | Buchungsverwaltung + Django-Admin (`/admin/`) |
| `EikeNonhoff`, `PeterFedders` | Gruppe `Verwaltung` | Buchungsliste + Stornierung, kein Django-Admin |

Neuen Verwaltungs-User der Gruppe zuweisen (im Django-Admin oder per Shell):
```python
from django.contrib.auth.models import User, Group
u = User.objects.get(username='<username>')
u.groups.add(Group.objects.get(name='Verwaltung'))
u.save()
```

---

## Umgebungsvariablen (`.env`)

| Variable | Beschreibung |
|---|---|
| `SECRET_KEY` | Django Secret Key |
| `DEBUG` | `False` im Produktivbetrieb |
| `ALLOWED_HOSTS` | `sportheim.westfalia-osterwick.de,89.167.0.28` |
| `MS_TENANT_ID` | Azure Tenant ID (Graph API) |
| `MS_CLIENT_ID` | Azure App Client ID |
| `MS_CLIENT_SECRET` | Azure App Client Secret |
| `MS_SENDER` | Absender-E-Mail (`sportheim@westfalia-osterwick.de`) |
| `NOTIFY_EMAIL` | Empfänger interner Benachrichtigungen |
