# Hosting-Optionen für die Vereinsheim-Buchung

## ❌ GitHub Pages ist NICHT geeignet

**Warum nicht?**
- GitHub Pages kann nur **statische HTML/CSS/JavaScript** Websites hosten
- Unser Projekt ist eine **Python FastAPI Backend-Anwendung** mit Server-Side Processing
- Wir brauchen eine Server-Umgebung für:
  - Microsoft Graph API-Anbindung
  - Sichere Speicherung von Secrets (Azure Credentials)
  - Python-Runtime und Abhängigkeiten

---

## ✅ Empfohlene Hosting-Optionen

### 1. **Koyeb** (KOSTENLOS ⭐ - EMPFOHLEN)
**Vorteile:**
- **Komplett kostenloser Plan verfügbar!**
- GitHub-Integration (Auto-Deploy)
- Automatische HTTPS
- Globales CDN
- Sehr einfaches Setup

**Kosten:** Kostenlos! (Eco Plan: 512 MB RAM, shared CPU)

**Setup:**
1. Gehe zu [koyeb.com](https://www.koyeb.com)
2. Login mit GitHub
3. "Create App" → "GitHub" → Repository auswählen
4. Build Command: `pip install -r backend/requirements.txt`
5. Run Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment Variables setzen
7. Deploy!

**Dateien vorbereiten:**
Erstelle `koyeb.yaml` im Root:
```yaml
app:
  name: vereinsheimbuchung
  services:
    - name: web
      instance_type: free
      regions:
        - fra
      build:
        builder: buildpack
        buildpack:
          build_command: pip install -r backend/requirements.txt
          run_command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
      ports:
        - port: 8000
          protocol: http
      env:
        - name: PORT
          value: 8000
```

---

### 2. **Render.com** (KOSTENLOS)
**Vorteile:**
- Kostenloser Free Tier
- Automatisches SSL
- GitHub Auto-Deploy
- Einfache Konfiguration

**Kosten:** Kostenlos (schläft nach Inaktivität, startet bei Zugriff)

**Setup:**
1. Gehe zu [render.com](https://render.com)
2. "New" → "Web Service"
3. Repository verbinden
4. Build Command: `pip install -r backend/requirements.txt`
5. Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment Variables setzen

**Hinweis:** Free Tier schläft nach 15 Min. Inaktivität (Kaltstart ~30 Sek.)

---

### 3. **Fly.io** (KOSTENLOS für kleine Apps)
**Vorteile:**
- Großzügiger Free Tier
- Sehr schnell
- Globales Netzwerk
- Docker-basiert

**Kosten:** Kostenlos bis 3 shared-CPU VMs (256MB RAM)

**Setup:**
```bash
# Fly CLI installieren
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# App erstellen und deployen
fly launch
```

---

### 4. **Railway.app** ⚠️ NICHT MEHR KOSTENLOS
**Vorteile:**
- Sehr einfaches Deployment
- Gute Developer Experience
- Automatische HTTPS

**Kosten:** Ab $5/Monat (Hobby Plan mit $5 Guthaben inkl.)

**Setup:** Siehe RAILWAY_DEPLOYMENT.md

---

### 5. **Azure Web App** (Beste Integration)
**Vorteile:**
- Nahtlose Integration mit Azure AD (nutzt du bereits)
- Professionell
- Skalierbar
- Gute Integration mit Microsoft-Ökosystem

**Kosten:** Ab ~13€/Monat (B1 Basic Plan)

**Setup:**
```bash
az login
az webapp up --name westfalia-vereinsheim --runtime "PYTHON:3.11" --sku B1
az webapp config appsettings set --name westfalia-vereinsheim \
  --settings AZURE_CLIENT_ID="..." AZURE_CLIENT_SECRET="..." AZURE_TENANT_ID="..."
```

---

### 6. **Eigener VPS/Server** (Günstigste Option langfristig)
**Optionen:**
- Hetzner Cloud (ab 4,15€/Monat)
- Contabo (ab 4,99€/Monat)
- Netcup (ab 2,99€/Monat)
- DigitalOcean Droplet (ab $6/Monat)

**Setup mit Docker:**
```dockerfile
# Dockerfile bereits vorhanden nutzen
docker build -t vereinsheim-buchung .
docker run -p 8000:8000 --env-file .env vereinsheim-buchung
```

**Vorteile:** Volle Kontrolle, günstig
**Nachteile:** Mehr Verwaltungsaufwand (Updates, Sicherheit, etc.)

---

## 📋 Deployment-Checkliste

Egal welche Option du wählst:

- [ ] `.env` Datei **NICHT** ins Git Repository committen
- [ ] In `.gitignore` eintragen: `.env`
- [ ] Umgebungsvariablen über Hosting-Plattform setzen
- [ ] SSL/HTTPS aktivieren (meist automatisch)
- [ ] Domain verbinden (optional, z.B. `buchung.westfalia-osterwick.de`)
- [ ] Monitoring aktivieren (um Ausfälle zu erkennen)
- [ ] Backup-Strategie überlegen

---

## 🚀 Schnellste kostenfreie Lösung: Koyeb

1. Gehe zu [koyeb.com](https://www.koyeb.com)
2. Login mit GitHub
3. "Create App" → "GitHub" → Repository `Crunchcow/Vereinsheimbuchung` wählen
4. Konfiguration:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Run Command:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Port:** 8000
5. Environment Variables hinzufügen:
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`
   - `AZURE_TENANT_ID`
   - `CALENDAR_ADDRESS`
   - `SENDER_EMAIL`
6. Deploy starten → Kostenlose URL erhalten!

**Fertig in 5 Minuten!** ⚡ **Komplett kostenlos!** 💰

---

## 💡 Meine Empfehlung

| Szenario | Empfehlung | Kosten |
|----------|-----------|--------|
| **Für den Start** | Koyeb oder Render.com | Kostenlos ✅ |
| **Hobby/Verein** | Koyeb (Always-on) | Kostenlos ✅ |
| **Professionell** | Azure Web App | ~13€/Monat |
| **Langfristig (>1 Jahr)** | Eigener VPS (Hetzner) | ~4€/Monat |
| **Maximale Einfachheit** | Koyeb | Kostenlos ✅ |

**Mein Tipp:** Starte mit **Koyeb** (kostenlos, einfach, zuverlässig)!
