from django.db import models

# Create your models here.
class Emission(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Füge einen Titel für die Emission hinzu'
        )
    beschreibung = models.TextField(
        max_length=1000,
        help_text='Füge eine Beschreibung der Emission hinzu'
        )
    wert = models.IntegerField(
        max_length=10,
        help_text='C02 Menge in Gramm'
        )
    kategorie = models.ForeignKey(
        'kategorie',
        on_delete=models.SET_NULL,
        null=True,
        help_text='Wähle eine Kategorie für die Emission'
        )

    def __str__(self):
        return self.name


class Kategorie(models.Model):
    name = models.CharField(
        max_length=200
        )

    def __str__(self):
        return self.name


class Frage(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Füge eine prägnante Frage hinzu (z.B.: Wie viele Flyer wurden gedruckt?)'
        )
    kategorie = models.ForeignKey(
        Kategorie,
        on_delete=models.SET_NULL,
        null=True,
        help_text='Wähle eine Kategorie für die Frage'
    )
