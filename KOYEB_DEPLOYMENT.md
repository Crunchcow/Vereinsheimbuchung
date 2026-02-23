# Koyeb Deployment Anleitung

## 🆓 Kostenfreies Deployment mit Koyeb

Koyeb bietet einen **komplett kostenlosen Plan** mit:
- 512 MB RAM
- Shared CPU
- Automatisches SSL/HTTPS
- Unbegrenzte Requests
- Keine Kreditkarte erforderlich
- Kein Sleep-Mode (Always-on!)

---

## ✅ Vorbereitungen

Die folgenden Dateien sind bereits vorbereitet:
- ✓ `koyeb.yaml` - Koyeb-Konfiguration (optional, kann auch via Dashboard konfiguriert werden)
- ✓ `requirements.txt` - Python-Abhängigkeiten
- ✓ `.gitignore` - .env wird nicht committed

---

## 🚀 Deployment-Schritte

### Methode 1: Via Web-Dashboard (Empfohlen für Anfänger)

#### 1. Koyeb Account erstellen
- Gehe zu [koyeb.com](https://www.koyeb.com)
- Klicke auf "Sign Up"
- Wähle "Continue with GitHub"
- Authorisiere Koyeb für dein GitHub-Konto
- **Keine Kreditkarte erforderlich!**

#### 2. Neue App erstellen
1. Klicke auf "Create App"
2. Wähle "GitHub" als Deployment-Methode
3. Wähle Repository: `Crunchcow/Vereinsheimbuchung`
4. Branch: `main`

#### 3. Build-Konfiguration
- **Builder:** Buildpack
- **Build Command:** 
  ```
  pip install -r backend/requirements.txt
  ```
- **Run Command:**
  ```
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

#### 4. Instance-Konfiguration
- **Instance Type:** Eco (Free)
- **Regions:** Frankfurt (fra) - am nächsten zu Deutschland
- **Scaling:** Min 1, Max 1

#### 5. Port-Konfiguration
- **Port:** 8000
- **Protocol:** HTTP
- **Public:** Ja

#### 6. Environment Variables setzen

**WICHTIG:** Klicke auf "+ Add Variable" und füge hinzu:

```
AZURE_CLIENT_ID=deine-azure-client-id
AZURE_CLIENT_SECRET=dein-azure-client-secret
AZURE_TENANT_ID=deine-azure-tenant-id
CALENDAR_ADDRESS=vereinsheim@westfalia-osterwick.de
SENDER_EMAIL=service@westfalia-osterwick.de
```

**Werte aus deiner lokalen `.env` Datei kopieren!**

#### 7. Deploy starten
1. Klicke auf "Deploy"
2. Warte 2-3 Minuten für Build und Deployment
3. Koyeb gibt dir eine URL wie: `https://vereinsheimbuchung-crunchcow.koyeb.app`

---

### Methode 2: Via Koyeb CLI (Für Fortgeschrittene)

```bash
# Koyeb CLI installieren
curl -fsSL https://cli.koyeb.com/install.sh | sh

# Login
koyeb login

# App deployen (nutzt koyeb.yaml)
koyeb app create vereinsheimbuchung

# Secrets setzen
koyeb secret create azure-client-id --value "deine-client-id"
koyeb secret create azure-client-secret --value "dein-secret"
koyeb secret create azure-tenant-id --value "deine-tenant-id"

# Deploy
koyeb service create web \
  --app vereinsheimbuchung \
  --git github.com/Crunchcow/Vereinsheimbuchung \
  --git-branch main \
  --git-build-command "pip install -r backend/requirements.txt" \
  --git-run-command "cd backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT" \
  --ports 8000:http \
  --routes /:8000 \
  --instance-type free \
  --regions fra \
  --env AZURE_CLIENT_ID=@azure-client-id \
  --env AZURE_CLIENT_SECRET=@azure-client-secret \
  --env AZURE_TENANT_ID=@azure-tenant-id \
  --env CALENDAR_ADDRESS=vereinsheim@westfalia-osterwick.de \
  --env SENDER_EMAIL=service@westfalia-osterwick.de
```

---

## 🔄 Automatische Updates

Nach dem initialen Setup:
- Jeder `git push` zu GitHub triggert automatisch ein neues Deployment
- Koyeb baut und deployed die neue Version
- Zero-Downtime Deployment
- Rollback möglich bei Fehlern

---

## 🌐 Custom Domain (Optional)

**Eigene Domain verbinden:**

1. Gehe zu App → "Settings" → "Domains"
2. Klicke auf "Add Domain"
3. Gib deine Domain ein: `buchung.westfalia-osterwick.de`
4. Erstelle DNS-Records bei deinem Provider:

**Option A - CNAME (Empfohlen):**
```
CNAME buchung → vereinsheimbuchung-crunchcow.koyeb.app
```

**Option B - A-Record:**
Koyeb zeigt dir die IP-Adressen an (z.B. `75.2.60.5`)
```
A     buchung → 75.2.60.5
```

5. SSL-Zertifikat wird automatisch erstellt (Let's Encrypt)

---

## 📊 Monitoring & Logs

**Logs ansehen:**
1. Dashboard → Deine App
2. Tab "Logs"
3. Real-time Logs oder filtern nach Zeitraum

**Metriken:**
- CPU-Auslastung
- RAM-Nutzung
- Network Traffic
- Request Count
- Response Times

Alles unter "Metrics" im Koyeb Dashboard verfügbar.

---

## 💰 Kosten & Limits

**Eco (Free) Tier:**
- ✅ **KOMPLETT KOSTENLOS**
- 512 MB RAM
- Shared CPU
- Unlimited Requests
- 100 GB Bandbreite/Monat
- 2.5 GB Docker image storage
- **Kein Sleep-Mode** (Always-on!)
- **Keine Kreditkarte erforderlich**

**Upgrade nur nötig wenn:**
- Mehr als 512 MB RAM benötigt
- Dedicated CPU gewünscht
- Mehr als 100 GB Traffic/Monat

---

## 🆘 Troubleshooting

### Build schlägt fehl
**Problem:** `ModuleNotFoundError: No module named 'xyz'`

**Lösung:**
1. Prüfe `backend/requirements.txt` - sind alle Dependencies drin?
2. Build Command korrekt: `pip install -r backend/requirements.txt`
3. Schaue in Build-Logs für Details

### App startet nicht
**Problem:** "Service unhealthy"

**Lösung:**
1. Run Command prüfen: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. Logs checken auf Python-Fehler
3. Environment Variables vollständig gesetzt?
4. Port 8000 in Koyeb konfiguriert?

### Health Check schlägt fehl
**Problem:** "Health check failed"

**Lösung:**
1. Stelle sicher, dass deine App auf `/` antwortet
2. Health Check Path: `/` (Standard)
3. Port: 8000
4. Grace Period auf 60 Sekunden setzen (für langsamen Start)

### Calendar API funktioniert nicht
**Problem:** 401 Unauthorized

**Lösung:**
1. Azure App Registration → Redirect URIs
2. Füge Koyeb-Domain hinzu: `https://<deine-app>.koyeb.app`
3. API Permissions prüfen (Calendars.ReadWrite, Mail.Send)
4. Environment Variables (AZURE_*) doppelt prüfen

### Zu wenig RAM
**Problem:** "Out of memory"

**Lösung:**
1. Free Tier hat 512 MB Limit
2. Optimiere Code (weniger simultane Requests)
3. Oder upgrade auf Nano Plan ($2.50/Monat mit 1 GB RAM)

---

## ✅ Post-Deployment Checkliste

Nach erfolgreichem Deployment testen:

- [ ] Hauptseite lädt (`https://<app>.koyeb.app`)
- [ ] Kalender wird angezeigt
- [ ] Verfügbarkeit wird geladen (API funktioniert)
- [ ] Formular kann abgesendet werden
- [ ] Bestätigungs-Email kommt an
- [ ] Termin erscheint im Outlook-Kalender
- [ ] Datenschutz-Seite ist erreichbar (`/datenschutz`)
- [ ] iCal-Download funktioniert
- [ ] Dark Mode toggle funktioniert
- [ ] Mobile Ansicht sieht gut aus
- [ ] HTTPS funktioniert (🔒 im Browser)

---

## 🔐 Sicherheit

**Best Practices:**
- ✓ Secrets nur über Koyeb Environment Variables
- ✓ .env Datei ist in .gitignore
- ✓ HTTPS wird automatisch von Koyeb bereitgestellt
- ✓ Azure Credentials haben minimale Rechte

**Empfohlen:**
- Nutze Koyeb Secrets für sensitive Daten
- Aktiviere GitHub Branch Protection
- Implementiere Rate Limiting in FastAPI (gegen Missbrauch)
- Überwache Logs auf verdächtige Aktivitäten

---

## 🔄 Vergleich zu anderen Anbietern

| Feature | Koyeb Free | Render Free | Railway | Fly.io Free |
|---------|-----------|-------------|---------|-------------|
| **Preis** | Kostenlos | Kostenlos | $5/Monat | Kostenlos |
| **RAM** | 512 MB | 512 MB | 512 MB | 256 MB |
| **CPU** | Shared | Shared | Shared | Shared |
| **Sleep** | Nein ✅ | Ja (15 Min) ❌ | Nein | Nein |
| **Bandbreite** | 100 GB | Unlimited | 100 GB | 160 GB |
| **Build Time** | ~2-3 Min | ~3-5 Min | ~2 Min | ~2-3 Min |
| **Regionen** | Global | US/EU | Global | Global |
| **SSL** | Auto ✅ | Auto ✅ | Auto ✅ | Auto ✅ |
| **GitHub Deploy** | Ja ✅ | Ja ✅ | Ja ✅ | Nein |

**Warum Koyeb:**
- ✅ Kein Sleep-Mode (Render schläft nach 15 Min!)
- ✅ Mehr RAM als Fly.io (512 MB vs 256 MB)
- ✅ Kostenlos (Railway kostet jetzt $5/Monat)
- ✅ Frankfurt-Region verfügbar (niedrige Latenz für Deutschland)
- ✅ Sehr gute Developer Experience

---

## 📞 Support

**Koyeb:**
- Docs: https://www.koyeb.com/docs
- Community: https://community.koyeb.com
- Status: https://status.koyeb.com
- Support: support@koyeb.com

**Bei Problemen:**
1. Prüfe Koyeb Logs im Dashboard
2. Teste lokal mit gleichen Environment Variables
3. Checke Environment Variables Schreibweise
4. Schaue in die Koyeb Community
5. Öffne Support-Ticket wenn nichts hilft

---

## 🎯 Nächste Schritte

Nach erfolgreichem Deployment:

1. **Teste alle Funktionen** (siehe Checkliste oben)
2. **Update Azure Redirect URI** mit Koyeb-URL
3. **Teile die URL** mit deinem Verein
4. **Überwache Logs** die ersten Tage
5. **Custom Domain** (optional) einrichten
6. **Backup-Strategie** überlegen (z.B. regelmäßiger Git-Push)

---

## 🚀 Deployment in 5 Minuten - Zusammenfassung

```bash
# 1. Code auf GitHub pushen
git add .
git commit -m "Prepare for Koyeb deployment"
git push origin main

# 2. Zu koyeb.com gehen
# - Mit GitHub anmelden
# - Repository verbinden
# - Build/Run Commands setzen
# - Environment Variables eintragen
# - Deploy klicken

# 3. Fertig! 🎉
```

**Deine App ist jetzt online unter:**
`https://vereinsheimbuchung-<dein-name>.koyeb.app`

**Komplett kostenlos, ohne Kreditkarte, ohne Sleep-Mode!** 🆓
