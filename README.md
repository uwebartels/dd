# dd anzeigen automatisch einstellen

## Voraussetungen:
- Python 3.3 oder größer
Python kommt auf dem Mac mit der Installation von Xcode mit

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
```
Letzte Zeilen sind der Text der Anzeige und kann sich über mehrere Zeilen erstrecken.
- Konfigurationsdatei dd.json wird automatisch erstellt, wenn sie nicht existiert. Hier werden login,password und Verzeichnis Eurer Anzeigen gespeichert.

- Skript ./anzeigen.py starten
Terminal starten
```
cd <Verzeichnis mit den von github ausgepackten Dateien>
./anzeigen.py

## was passiert?
- es werden alle anzeigen aus dem Account gelöscht
- alle Anzeigen in dem Verzeichnis werden neu erstellt


## Todo's / bekannte Probleme:
- Auswahl der Kategorie
  Beschränkt Euch hier auf einen eindeutigen Teilstring ohne Sonderzeichen und Umlauten. Hier muss ich auf Python 3.6 warten, dann geht automatisch mehr.
