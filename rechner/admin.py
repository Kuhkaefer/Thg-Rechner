from django.contrib import admin
from .models import Category, Emission, Question, EventTemplate, DefaultAmount, Source, CalculationFactor

# Register your models here.
admin.site.register(Category)
admin.site.register(Source)


class SourceAdminInline(admin.TabularInline):
    model = Emission.source.through


@admin.register(Emission)
class EmissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'value', 'source', 'unit', 'explanation')
        }),
    )
    search_fields = ['name', 'value', 'source', 'unit', 'explanation']

class DefaultAmountsInline(admin.TabularInline):
    model = DefaultAmount

class FactorsInline(admin.TabularInline):
    model = CalculationFactor


@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    inlines = [DefaultAmountsInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [FactorsInline]
