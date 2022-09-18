from django.contrib import admin
from .models import Category, Emission, Question, EventTemplate, DefaultAmount, \
Source, CalculationFactor, EmissionFactor, Advice
from django.db.models.functions import Lower


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields=["name"]
    ordering=["name"]

@admin.register(Emission)
class EmissionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering=["name"]
    autocomplete_fields=["source"]

class CFactorsInline(admin.TabularInline):
    model = CalculationFactor
    autocomplete_fields = ['emission']
    extra=10

@admin.register(EmissionFactor)
class EFactorsInline(admin.ModelAdmin):
    autocomplete_fields = ['source']
    def get_ordering(self, request):
        return [Lower('name')]


class DefaultAmountsInline(admin.TabularInline):
    model = DefaultAmount
    autocomplete_fields = ['question']
    extra=10

@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    inlines = [DefaultAmountsInline]
    def get_ordering(self, request):
        return [Lower('name')]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [CFactorsInline]
    def get_ordering(self, request):
        return [Lower('name')]

    search_fields = ["name"]

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    def get_ordering(self, request):
        return [Lower('name')]

@admin.register(Advice)
class AdviceAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user_q", "suggested_q", "source"]
    def get_ordering(self, request):
        return [Lower('user_q__name'),Lower('suggested_q__name')]
