from django.contrib import admin
from .models import Category, Emission, Question, EventTemplate, DefaultAmount, \
Source, CalculationFactor, EmissionFactor, Advice
from django.db.models.functions import Lower


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields=["name"]
    ordering=["name"]
    readonly_fields=('pk',)
    list_display = ["name", "pk"]

@admin.register(Emission)
class EmissionAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering=["name"]
    autocomplete_fields=["source"]
    readonly_fields=('pk',)
    list_display = ["name", "pk", "unit", "value"]

class CFactorsInline(admin.TabularInline):
    model = CalculationFactor
    autocomplete_fields = ['emission']
    extra=6
    readonly_fields=('pk',)
    search_fields = ['name']

@admin.register(EmissionFactor)
class EFactorsInline(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['source']
    readonly_fields=('pk',)
    list_display = ["name", "pk", "unit", "value"]
    def get_ordering(self, request):
        return [Lower('name')]

class DefaultAmountsInline(admin.TabularInline):
    model = DefaultAmount
    autocomplete_fields = ['question']
    extra=10
    readonly_fields=('pk',)

@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [DefaultAmountsInline]
    readonly_fields=('pk',)
    list_display = ["name", "pk"]
    def get_ordering(self, request):
        return [Lower('name')]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [CFactorsInline]
    search_fields = ['name']
    readonly_fields=('pk',)
    list_display = ["name", "pk","question_text"]
    def get_ordering(self, request):
        return [Lower('name')]

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "pk", "url"]
    readonly_fields=('pk',)
    def get_ordering(self, request):
        return [Lower('name')]

@admin.register(Advice)
class AdviceAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user_q", "suggested_q", "source"]
    readonly_fields=('pk',)
    list_display = ['__str__', "pk", 'suggested_f']
    search_fields = ["user_q__name"]
    def get_ordering(self, request):
        return [Lower('user_q__name'),Lower('suggested_q__name')]
