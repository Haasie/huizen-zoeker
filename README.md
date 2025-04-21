# Huizenzoeker - Dutch Real Estate Scraper

Huizenzoeker is een applicatie die meerdere Nederlandse vastgoedwebsites scant op nieuwe of gewijzigde woningaanbiedingen en je hierover informeert via Telegram.

## Functionaliteiten

- **Automatisch scannen** van 15 Nederlandse vastgoedwebsites
- **Prijsfiltering** tussen €100.000 en €225.000
- **Realtime meldingen** via Telegram voor nieuwe, gewijzigde en verwijderde woningen
- **Webinterface** in het Nederlands voor het bekijken en beheren van woningaanbiedingen
- **Configureerbaar** via YAML of JSON configuratiebestand
- **Docker-ondersteuning** voor eenvoudige installatie en gebruik

## Installatie

### Vereisten

- Docker en Docker Compose
- Telegram Bot API-sleutel (standaard meegeleverd: `8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA`)
- Telegram Chat ID (moet je zelf configureren)

### Installatie met Docker

1. Clone de repository of download de bestanden
2. Navigeer naar de hoofdmap van het project
3. Start de applicatie met Docker Compose:

```bash
docker-compose up -d
```

De webinterface is nu beschikbaar op `http://localhost:5000`

### Handmatige installatie

Als je de applicatie zonder Docker wilt gebruiken:

1. Zorg ervoor dat Python 3.10 of hoger is geïnstalleerd
2. Installeer de vereiste packages:

```bash
pip install -r requirements.txt
```

3. Installeer Playwright browsers:

```bash
playwright install chromium
```

4. Start de applicatie:

```bash
python main.py
```

## Configuratie

De applicatie kan worden geconfigureerd via het `config.yaml` bestand. Hieronder staan de belangrijkste configuratie-opties:

### Algemene instellingen

```yaml
general:
  scan_interval: 30  # Scan interval in minuten
  log_level: INFO    # Log niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  database_path: huizenzoeker.db  # Pad naar de database
```

### Filter instellingen

```yaml
filter:
  min_price: 100000  # Minimale prijs
  max_price: 225000  # Maximale prijs
  min_area: 0        # Minimale oppervlakte in m²
  cities: []         # Lijst van steden om te filteren (leeg = alle steden)
  property_types: [] # Lijst van woningtypes om te filteren (leeg = alle types)
```

### Telegram instellingen

```yaml
telegram:
  token: "8169156824:AAG0Nz-OrByEWWjaCaDw6FaLVMCh3_lgnaA"  # Telegram Bot API-sleutel
  chat_id: ""        # Jouw Telegram Chat ID
  notify_new: true   # Meldingen voor nieuwe woningen
  notify_updated: true  # Meldingen voor gewijzigde woningen
  notify_removed: true  # Meldingen voor verwijderde woningen
  send_summary: true    # Samenvattende melding na elke scan
```

### Websites instellingen

```yaml
websites:
  klipenvw: true
  bijdevaate: true
  ooms: true
  vbrmakelaars: true
  ruimzicht: true
  visiemakelaardij: true
  voornemakelaars: true
  marquis: true
  rozenburgmakelaardij: true
  deltamakelaardij: true
  dehuizenbemiddelaar: true
  kolpavanderhoek: true
  rijnmondmakelaars: true
  woonvoorn: true
  boogerman: true
```

### GUI instellingen

```yaml
gui:
  enabled: true      # Web GUI inschakelen
  host: "0.0.0.0"    # Host om te binden
  port: 5000         # Poort om te binden
  debug: false       # Debug modus
```

## Gebruik

### Webinterface

De webinterface is beschikbaar op `http://localhost:5000` en biedt de volgende functionaliteiten:

- **Dashboard**: Overzicht van recente activiteit en statistieken
- **Woningen**: Lijst van alle woningen met filter- en zoekfunctionaliteit
- **Instellingen**: Configuratie van de applicatie

### Telegram meldingen

Om Telegram meldingen te ontvangen:

1. Start een chat met de Telegram bot (gebruik de link `t.me/jouw_bot_naam`)
2. Verkrijg je Chat ID door het commando `/start` te sturen naar de bot
3. Configureer je Chat ID in de instellingen

### Commando's

De applicatie ondersteunt de volgende commando's:

```bash
# Start de applicatie
python main.py

# Start met aangepast configuratiebestand
python main.py --config mijn_config.yaml

# Voer de scraper eenmalig uit en sluit af
python main.py --run-once

# Start zonder webinterface
python main.py --no-gui
```

## Ondersteunde websites

De applicatie ondersteunt de volgende Nederlandse vastgoedwebsites:

1. klipenvw.nl
2. bijdevaatemakelaardij.nl
3. ooms.com
4. vbrmakelaars.nl
5. ruimzicht.nl
6. visiemakelaardij.nl
7. voornemakelaars.nl
8. marquis.nl
9. rozenburgmakelaardij.nl
10. deltamakelaardij.nl
11. dehuizenbemiddelaar.nl
12. kolpavanderhoek.nl
13. rijnmondmakelaars.nl
14. woonvoorn.nl
15. boogerman.nl

## Probleemoplossing

### Veelvoorkomende problemen

1. **Geen Telegram meldingen**:
   - Controleer of je de juiste Telegram Bot API-sleutel hebt geconfigureerd
   - Controleer of je de juiste Chat ID hebt geconfigureerd
   - Controleer of je chat hebt gestart met de bot

2. **Geen woningen gevonden**:
   - Controleer of de websites zijn ingeschakeld in de configuratie
   - Controleer of je prijsfilter niet te restrictief is
   - Controleer de logs op fouten tijdens het scrapen

3. **Webinterface niet beschikbaar**:
   - Controleer of de applicatie draait
   - Controleer of de juiste poort is geconfigureerd en beschikbaar is
   - Controleer of de GUI is ingeschakeld in de configuratie

### Logs bekijken

De applicatie schrijft logs naar `huizenzoeker.log`. Bekijk deze voor gedetailleerde informatie over de werking van de applicatie en eventuele fouten.

## Ontwikkelaarshandleiding

### Projectstructuur

```
huizenzoeker/
├── config/             # Configuratie module
├── database/           # Database module
├── gui/                # Web GUI module
├── notification/       # Telegram notificatie module
├── scrapers/           # Website scrapers
└── utils/              # Hulpprogramma's (filters, logging, etc.)
```

### Nieuwe scraper toevoegen

Om een nieuwe vastgoedwebsite toe te voegen:

1. Maak een nieuwe scraper klasse in `huizenzoeker/scrapers/`
2. Laat de klasse erven van `BaseScraper`
3. Implementeer de `get_listings` methode
4. Voeg de scraper toe aan `__init__.py`
5. Voeg de website toe aan de configuratie

### Tests uitvoeren

```bash
python -m unittest discover tests
```

## Licentie

Dit project is gelicenseerd onder de MIT-licentie.
