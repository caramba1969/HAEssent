# Essent Dynamic Pricing voor Home Assistant

Deze Home Assistant Custom Component haalt de dynamische stroom- en gasprijzen op van Essent.

Door een recente beveiligingsupdate bij Essent werken de publieke/openbare endpoints niet meer zonder een specifieke `x-request-origin: client` header. Deze integratie voegt deze header netjes toe en haalt elk uur de actuele tarieven op, inclusief de data voor vandaag en morgen (handig voor bijvoorbeeld ApexCharts).

## Sensoren

De volgende sensoren worden aangemaakt:
- `sensor.essent_dynamic_electricity_price` (actuele prijs per kWh)
- `sensor.essent_dynamic_gas_price` (actuele prijs per m³)

Beide sensoren bevatten attributen met de prijzen voor `today` en `tomorrow` in JSON formaat.

## Installatie via HACS (Custom Repository)

1. Open Home Assistant en ga naar **HACS**.
2. Klik in de rechterbovenhoek op de drie puntjes en kies **Custom repositories**.
3. Vul bij **Repository** de URL van deze GitHub repository in.
4. Kies bij **Category** voor `Integration`.
5. Klik op **Add**.
6. Zoek nu in HACS naar "Essent Dynamic Pricing" en klik op **Download**.
7. Herstart Home Assistant.

## Configuratie

Na de herstart kun je de integratie toevoegen via de Home Assistant UI:
1. Ga naar **Instellingen** -> **Apparaten & Diensten**.
2. Klik rechtsonder op **Integratie toevoegen**.
3. Zoek op "Essent Dynamische Prijzen" (of "Essent Dynamic Pricing" als je taal op Engels staat).
4. Klik erop om de configuratie af te ronden. Je hebt hiervoor verder geen account of inloggegevens nodig.
