# Vereinsheim-Buchung - Benutzerhandbuch

## Projektübersicht

Die **Vereinsheim-Buchung** ist ein modernes webbasiertes System zur Reservierung des Vereinsheims. Es ersetzt die bisherige Power Automate Lösung und bietet eine benutzerfreundliche Oberfläche mit direkter Microsoft 365 Integration.

---

## Für Benutzer (Vereinsmitglieder)

### Zugang zur Buchung
- **URL:** `https://[domain]/`
- **Login:** Über Microsoft-Konto (Azure AD)

### Buchung durchführen

#### 1. Anmeldung
1. Webseite aufrufen
2. "Anmelden" klicken
3. Microsoft-Konto-Anmeldung
4. Automatische Weiterleitung zur Buchungsoberfläche

#### 2. Verfügbarkeit prüfen
1. **Datum auswählen:** Kalender anklicken
2. **Uhrzeit wählen:** Verfügbare Zeiten werden grün angezeigt
3. **Dauer festlegen:** Standard 2 Stunden, anpassbar
4. **Belegung einsehen:** Aktuelle Buchungen werden angezeigt

#### 3. Buchungsdetails eingeben
1. **Veranstaltung:** Art der Veranstaltung auswählen
   - Vereinsversammlung
   - Geburtstagsfeier
   - Training/Schulung
   - Sonstiges

2. **Teilnehmerzahl:** Erwartete Gästeanzahl
3. **Beschreibung:** Zusätzliche Informationen
4. **Kontaktdaten:** Telefonnummer für Rückfragen

#### 4. Buchung bestätigen
1. Daten prüfen
2. "Buchen" Button klicken
3. Automatische Bestätigungs-E-Mail
4. Kalendereintrag wird erstellt

### Buchung bearbeiten/stornieren
1. Eigene Buchungen im Dashboard anzeigen
2. "Bearbeiten" oder "Stornieren" klicken
3. Änderungen bestätigen
4. Automatische Benachrichtigung aller Teilnehmer

---

## Für Administratoren und Verwalter

### Admin-Zugang
- **URL:** `https://[domain]/admin/`
- **Login:** Mit Admin-Rechten über Microsoft-Konto

### Hauptfunktionen

#### 1. Buchungsübersicht
- Alle Buchungen einsehen
- Nach Datum/Benutzer filtern
- Buchungsstatistiken anzeigen
- Konflikte erkennen

#### 2. Kalenderverwaltung
- Microsoft 365 Kalender-Integration
- Automatische Synchronisation
- Mehrere Kalender unterstützen
- Feiertage automatisch berücksichtigen

#### 3. Benutzerverwaltung
- Berechtigungen verwalten
- Buchungslimits festlegen
- Sondergenehmigungen erteilen
- Benutzerstatistiken

#### 4. Systemeinstellungen
- Buchungsregeln konfigurieren
- E-Mail-Vorlagen anpassen
- Benachrichtigungseinstellungen
- Integrationen verwalten

---

## Buchungsregeln und -richtlinien

### Allgemeine Regeln
- **Vorlaufzeit:** Mindestens 14 Tage im Voraus buchbar
- **Maximale Dauer:** 4 Stunden pro Buchung
- **Gleichzeitige Buchungen:** Nicht möglich
- **Stornierung:** Bis 48 Stunden vor Beginn kostenlos

### Veranstaltungsarten
**Erlaubt:**
- Vereinsinterne Veranstaltungen
- Mitgliederversammlungen
- Trainings und Schulungen
- Private Feiern von Mitgliedern

**Eingeschränkt:**
- Kommerzielle Veranstaltungen
- Politische Veranstaltungen
- Veranstaltungen über 100 Personen

### Zeitliche Einschränkungen
- **Wochentage:** 8:00 - 22:00 Uhr
- **Wochenenden:** 9:00 - 23:00 Uhr
- **Feiertage:** Besondere Regelungen
- **Saisonzeiten:** Sommer/Winter-Zeiten

---

## Wichtige Prozesse

### Buchungsgenehmigung
1. Benutzer stellt Buchungsanfrage
2. System prüft Verfügbarkeit und Regeln
3. Automatische Genehmigung bei Standardfällen
4. Manuelle Prüfung bei Sonderfällen

### Konfliktlösung
1. System erkennt doppelte Buchungen
2. Automatische Benachrichtigung aller Beteiligten
3. Admin entscheidet über Priorität
4. Alternative Termine vorschlagen

### Notfallbuchungen
1. Admin kann kurzfristige Buchungen genehmigen
2. Sonderregelungen dokumentieren
3. Alle betroffenen Benutzer informieren

---

## Microsoft 365 Integration

### Kalender-Synchronisation
- Automatische Erstellung von Outlook-Terminen
- Einladungen an alle Teilnehmer
- Erinnerungen automatisch versenden
- Abwesenheiten berücksichtigen

### E-Mail-Benachrichtigungen
- Buchungsbestätigungen
- Stornierungsbenachrichtigungen
- Erinnerungen an bevorstehende Veranstaltungen
- Änderungsmeldungen

### Authentifizierung
- Single Sign-On mit Microsoft-Konto
- Automatische Benutzererkennung
- Rollenbasierte Berechtigungen
- Sichere Anmeldung ohne zusätzliche Passwörter

---

## Mobile Nutzung

### Responsive Design
- Volle Funktionalität auf Smartphones und Tablets
- Touch-optimierte Bedienung
- Schnelle Ladezeiten auch mobil

### Mobile Features
- Kalenderintegration mit Smartphone-Kalender
- Push-Benachrichtigungen
- Offline-Buchungsübersicht
- QR-Code für schnellen Zugang

---

## Fehlerbehebung

### Häufige Probleme

**"Login nicht möglich"**
- Microsoft-Konto prüfen
- Internetverbindung stabil?
- Browser-Cache leeren
- Alternative Browser versuchen

**"Buchung nicht möglich"**
- Verfügbarkeit prüfen
- Zeitformat korrekt?
- Alle Pflichtfelder ausgefüllt?
- Buchungsregeln prüfen

**"E-Mail nicht erhalten"**
- Spam-Ordner prüfen
- Microsoft 365 Postfach prüfen
- E-Mail-Adresse korrekt?
- Postfach voll?

**"Kalender nicht synchronisiert"**
- Microsoft 365 Verbindung prüfen
- Berechtigungen überprüfen
- Admin kontaktieren
- Manuelles Synchronisieren versuchen

---

## Administrationsaufgaben

### Tägliche Aufgaben
- Neue Buchungen prüfen
- Konflikte lösen
- Benutzeranfragen bearbeiten
- Systemstatus überwachen

### Wöchentliche Aufgaben
- Statistiken auswerten
- Auslastung analysieren
- Benutzerfeedback sammeln
- System-Performance prüfen

### Monatliche Aufgaben
- Backup durchführen
- Benutzerkonten pflegen
- Buchungsregeln überprüfen
- Microsoft 365 Integration prüfen

---

## Sicherheit und Datenschutz

### Datensicherheit
- Azure AD Authentifizierung
- SSL-Verschlüsselung
- Regelmäßige Backups
- Zugriffskontrollen

### Datenschutz
- DSGVO-konforme Verarbeitung
- Minimale Datenerhebung
- Einwilligungen dokumentiert
- Löschfristen beachtet

### Microsoft 365 Sicherheit
- Unternehmensweite Sicherheitsrichtlinien
- Multi-Faktor-Authentifizierung
- Bedingter Zugriff
- Datenschutz-Audits

---

## Technische Informationen

### Systemarchitektur
- **Backend:** FastAPI mit Python
- **Frontend:** Jinja Templates (später React geplant)
- **Authentifizierung:** Microsoft Graph API via MSAL
- **Kalender:** Microsoft 365 Exchange Online
- **Datenbank:** Azure SQL (geplant)

### Anforderungen
- Moderner Webbrowser
- Microsoft 365 Konto
- Internetverbindung
- JavaScript aktiviert

### Wartung
- Automatische Updates
- Monitoring und Logging
- Performance-Optimierung
- Security-Patches

---

## Support und Hilfe

### Technischer Support
Bei Systemproblemen:
- IT-Abteilung des Vereins
- Microsoft 365 Support
- Screenshot des Fehlers machen
- Browser und Version angeben

### Inhaltliche Fragen
Bei organisatorischen Fragen:
- Vereinsheim-Verwalter
- Vorstand
- Geschäftsführung

### Notfallkontakte
- Akute Buchungsprobleme: Vereinsheim-Verwalter
- Systemausfall: IT-Support
- Microsoft 365 Probleme: IT-Abteilung

---

## Best Practices

### Für Benutzer
- Frühzeitig buchen
- Änderungen sofort mitteilen
- Regeln beachten
- Rückfragen stellen

### Für Administratoren
- Regelmäßige Kontrollen
- Schnelle Bearbeitung
- Dokumentation pflegen
- Benutzer schulen

---

## Zukunftsentwicklungen

### Geplante Funktionen
- Mobile App (iOS/Android)
- Erweiterte Statistiken
- Automatische Abrechnung
- Raumausstattung buchbar

### Roadmap
- Q2 2026: Mobile App
- Q3 2026: Erweiterte Reporting
- Q4 2026: Zahlungsfunktionen
- Q1 2027: Multi-Raum-Unterstützung

---

## Rechtliche Hinweise

### Haftung
- Nutzung auf eigene Gefahr
- Verein haftet für ordnungsgemäßen Zustand
- Benutzer haften für verursachte Schäden

### Nutzungsbedingungen
- Buchungen sind verbindlich
- Sauberkeit und Ordnung erforderlich
- Hausordnung ist zu beachten
- Missbrauch wird geahndet

### Microsoft 365
- Nutzung unterliegt Microsoft-Lizenzbedingungen
- Datenverarbeitung in Microsoft-Cloud
- Unternehmensrichtlinien gelten

---

*Letzte Aktualisierung: April 2026*
