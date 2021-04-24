from django.contrib import admin

# Register your models here.
from .models import Emission, Kategorie, Frage, Veranstaltungstyp

admin.site.register(Emission)
admin.site.register(Kategorie)
admin.site.register(Frage)
admin.site.register(Veranstaltungstyp)
