# dd anzeigen automatisch einstellen

## Voraussetungen:
- Python 3.3 oder größer
Hier steht, wie es geht
http://docs.python-guide.org/en/latest/starting/install3/osx/

## Installation
- als ZIP herunterladen und auspacken

## wie geht's?
- Verzeichnis mit den Anzeigen erstellen
- pro Anzeige darin ein Verzeichnis erstellen
- Bilder im Verzeichnis anlegen, die ersten 3 Bilder werden genommen
- Datei text.txt erstellen und in folgendem Format erstellen
```
Titel: Tabou 48 cm PB
Preis: 40
Kategorie: Finnen
Ort: Berlin
Reserviert: Ja
Freeride Finne, fast wie neu.
Versand möglich, zusätzlich 5 EUR
```
Letzte Zeilen sind der Text der Anzeige und kann sich über mehrere Zeilen erstrecken.
- Konfigurationsdatei dd.json erstellen:
{
    "anzeigenpath": "/Users/uwe/Desktop/dd/active", 
    "username": "<dd kleinanazeigen login>", 
    "password": "<dd kleinanzeigen passwort>"
}
Wer anzeigen.py per Terminal starten kann, dem wird hier das Anlegen der Datei erspart.

- unter Windows Skript anzeigen.py starten
- unter Mac dd.app starten. Die Logdatei ist dann anzeigen.log

## was passiert?
- es werden alle anzeigen aus dem Account gelöscht
- alle Anzeigen in dem Verzeichnis werden neu erstellt


## Todo's / bekannte Probleme:
- Auswahl der Kategorie
  Beschränkt Euch hier auf einen eindeutigen Teilstring ohne Sonderzeichen und Umlauten. Hier muss ich auf Python 3.6 warten, dann geht automatisch mehr.
