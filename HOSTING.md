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

### 1. **Azure Web App** (EMPFOHLEN ⭐)
**Vorteile:**
- Nahtlose Integration mit Azure AD (nutzt du bereits)
- Einfache Umgebungsvariablen-Verwaltung
- Automatische SSL-Zertifikate
- Skalierbar
- Gute Integration mit Microsoft-Ökosystem

**Kosten:** Ab ~13€/Monat (B1 Basic Plan)

**Setup:**
```bash
# Azure CLI installieren und einloggen
az login

# Web App erstellen
az webapp up --name westfalia-vereinsheim --runtime "PYTHON:3.11" --sku B1

# Umgebungsvariablen setzen
az webapp config appsettings set --name westfalia-vereinsheim \
  --settings AZURE_CLIENT_ID="..." AZURE_CLIENT_SECRET="..." AZURE_TENANT_ID="..."
```

---

### 2. **Railway.app**
**Vorteile:**
- Sehr einfaches Deployment (GitHub-Integration)
- Kostenloser Starter-Plan
- Automatische HTTPS
- Gute Developer Experience

**Kosten:** Kostenlos für kleine Projekte, dann ab $5/Monat

**Setup:**
1. Über GitHub Account anmelden
2. Repository verbinden
3. Environment Variables setzen
4. Automatisches Deployment bei jedem Git Push

---

### 3. **Heroku**
**Vorteile:**
- Bekannt und stabil
- Einfaches Deployment
- Add-ons verfügbar

**Kosten:** Ab $7/Monat (Eco Dyno)

**Setup:**
```bash
# Heroku CLI installieren
heroku login

# App erstellen
heroku create westfalia-vereinsheim

# Environment Variables setzen
heroku config:set AZURE_CLIENT_ID="..."

# Deployen
git push heroku main
```

---

### 4. **DigitalOcean App Platform**
**Vorteile:**
- Gutes Preis-Leistungs-Verhältnis
- Einfache Skalierung
- Gute Performance

**Kosten:** Ab $5/Monat

---

### 5. **Eigener VPS/Server (für Fortgeschrittene)**
**Optionen:**
- Hetzner Cloud (ab 4,15€/Monat)
- Contabo (ab 4,99€/Monat)
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

## 🚀 Schnellste Lösung: Railway

1. Gehe zu [railway.app](https://railway.app)
2. "Start a New Project" → "Deploy from GitHub repo"
3. Repository auswählen
4. Environment Variables hinzufügen:
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`
   - `AZURE_TENANT_ID`
   - `CALENDAR_ADDRESS`
   - `SENDER_EMAIL`
5. Deploy starten → URL erhalten

**Fertig in 5 Minuten!** ⚡

---

## 💡 Meine Empfehlung

**Für den Start:** Railway.app (kostenlos, einfach)  
**Langfristig:** Azure Web App (bessere Integration mit eurem Microsoft-Setup)
