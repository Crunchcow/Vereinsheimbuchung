# Railway Deployment Anleitung

## ✅ Vorbereitungen

Die folgenden Dateien sind bereits vorbereitet:
- ✓ `Procfile` - Start-Befehl für Railway
- ✓ `railway.toml` - Railway-Konfiguration
- ✓ `requirements.txt` - Python-Abhängigkeiten
- ✓ `.gitignore` - .env wird nicht committed

---

## 🚀 Deployment-Schritte

### 1. Railway Account erstellen
- Gehe zu [railway.app](https://railway.app)
- Klicke auf "Login" und wähle "GitHub"
- Authorisiere Railway für dein GitHub-Konto

### 2. Neues Projekt erstellen
1. Klicke auf "New Project"
2. Wähle "Deploy from GitHub repo"
3. Wähle das Repository `Crunchcow/Vereinsheimbuchung`
4. Railway erkennt automatisch Python und startet das Deployment

### 3. Environment Variables setzen

**WICHTIG:** Alle Secrets müssen in Railway gesetzt werden!

Klicke auf dein Projekt → "Variables" → Füge folgende hinzu:

```
AZURE_CLIENT_ID=deine-azure-client-id
AZURE_CLIENT_SECRET=dein-azure-client-secret
AZURE_TENANT_ID=deine-azure-tenant-id
CALENDAR_ADDRESS=vereinsheim@westfalia-osterwick.de
SENDER_EMAIL=service@westfalia-osterwick.de
```

**Werte aus deiner `.env` Datei kopieren!**

### 4. Domain konfigurieren (Optional)

Railway gibt dir automatisch eine Domain wie:
`https://vereinsheimbuchung-production.up.railway.app`

**Eigene Domain verbinden:**
1. Klicke auf "Settings" → "Domains"
2. Klicke auf "Custom Domain"
3. Gib deine Domain ein (z.B. `buchung.westfalia-osterwick.de`)
4. Erstelle einen CNAME-Record bei deinem DNS-Provider:
   ```
   CNAME buchung → <railway-domain>
   ```

### 5. Deployment überwachen

1. Klicke auf "Deployments" um den Build-Prozess zu sehen
2. Warte bis Status "Success" angezeigt wird
3. Teste deine App unter der generierten URL

---

## 🔄 Automatische Updates

Nach dem initialen Setup:
- Jeder `git push` zu GitHub triggert automatisch ein neues Deployment
- Railway baut und deployed die neue Version automatisch
- Alte Version läuft weiter, bis neue bereit ist (Zero Downtime)

---

## 📊 Monitoring & Logs

**Logs ansehen:**
1. Klicke auf dein Projekt
2. Wähle "Deployments" → Aktuellstes Deployment
3. Klicke auf "View Logs"

**Metriken:**
- CPU-Auslastung
- RAM-Nutzung
- Request-Anzahl
- Response-Zeiten

Alles unter "Metrics" im Railway Dashboard

---

## 💰 Kosten

**Free Tier:**
- $5 Guthaben pro Monat
- Perfekt für kleine Vereins-Projekte
- Reicht für ~500 Stunden Laufzeit

**Developer Plan:** $5/Monat
- $5 Guthaben + Pay-as-you-go
- Für mehr Traffic oder 24/7 Laufzeit

**Pro Plan:** $20/Monat
- Bessere Performance
- Priority Support

---

## 🆘 Troubleshooting

### Build schlägt fehl
**Problem:** `ModuleNotFoundError: No module named 'xyz'`
**Lösung:** Prüfe, ob alle Dependencies in `requirements.txt` stehen

### App startet nicht
**Problem:** "Application failed to respond"
**Lösung:** 
1. Prüfe Logs auf Python-Fehler
2. Stelle sicher, dass alle Environment Variables gesetzt sind
3. Teste lokal mit: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Calendar API funktioniert nicht
**Problem:** 401 Unauthorized oder 403 Forbidden
**Lösung:**
1. Prüfe Azure App Registration Redirect URIs
2. Füge Railway-Domain hinzu: `https://<deine-app>.railway.app`
3. API Permissions in Azure AD prüfen

### Timeout bei Requests
**Problem:** Requests dauern zu lange
**Lösung:**
1. Erhöhe `healthcheckTimeout` in `railway.toml`
2. Optimiere Graph API Queries
3. Implementiere Caching

---

## ✅ Post-Deployment Checkliste

Nach erfolgreichem Deployment testen:

- [ ] Hauptseite lädt korrekt
- [ ] Kalender wird angezeigt
- [ ] Verfügbarkeit wird geladen
- [ ] Formular kann abgesendet werden
- [ ] Bestätigungs-Email kommt an
- [ ] Termin erscheint im Outlook-Kalender
- [ ] Datenschutz-Seite ist erreichbar
- [ ] iCal-Download funktioniert
- [ ] Dark Mode funktioniert
- [ ] Mobile Ansicht sieht gut aus

---

## 🔐 Sicherheit

**Best Practices:**
- ✓ Secrets nur über Railway Environment Variables
- ✓ .env Datei ist in .gitignore
- ✓ HTTPS wird automatisch von Railway bereitgestellt
- ✓ Azure Credentials haben minimale Rechte

**Empfohlen:**
- Aktiviere "Require Redeployment for Environment Changes"
- Nutze Railway's "Private Networking" für Datenbanken
- Implementiere Rate Limiting in FastAPI

---

## 📞 Support

**Railway:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

**Bei Problemen:**
1. Prüfe Railway Logs
2. Teste lokal
3. Checke Environment Variables
4. Schaue ins Railway Discord
