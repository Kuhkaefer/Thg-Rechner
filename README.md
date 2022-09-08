# Info

- Todos/Challenges: https://demo.hedgedoc.org/G8wkoCRxR_6neQGpLeeo2g?view
- Good to know: https://demo.hedgedoc.org/6KghLKhrTr-tYJCRrI9hfA#


# Models
- Beschreibung von Struktur von Dingen, die in Datenbank gespeichert werden sollen.
- Admin kann Instanzen dieser Modelle erzeugen, und diese in der Datenbank abspeicher.

# Forms
- Möglichkeit, um Instanzen von Models zu bearbeiten
- Klassenahn, von dem geerbt wird
- In Form werden Felder definiert
- wird in views importiert. view zeigt form an.
- Forms haben nichts mit Datenbank zu tun
- Forms lassen sich leicht in html "drucken". mit forms.to_table. Dann wird für jedes Objekt der Form der Name des Objects und das Feld angezeigt. (name = models.Charfield()). Wir wollen aber, dass der String in dem Objekt agezeigt wird.

# Model Forms
- Forms, die Felder von Modellen verwenden
- Damit kann man auch eine Instanz eines Modells verändern

# Views
- Funktionen in APPNAME/views.py
- Berechnungen, Datenauslese, etc
- Render Daten in Template. Oder return HTTP response
- Auswahl eines Templates und der Daten, die darin gerendert werden sollen

# Ordnerstruktur:
- Überordner:   thg-webapp (startproject)
- Python-Packet für Projekt: Unterordner thg-webapp (startproject)
- Web-Application: rechner (startapp)
