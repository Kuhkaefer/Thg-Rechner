from django.contrib import admin
from .models import Category, Emission, Question, Calculation, EventTemplate, DefaultAmounts, Source

# Register your models here.
admin.site.register(Category)
admin.site.register(Source)


class SourceAdminInline(admin.TabularInline):
    model = Emission.source.through


@admin.register(Emission)
class EmissionAdmin(admin.ModelAdmin):
    inlines = [SourceAdminInline]
    # list_display = ['name', 'emission']
    fieldsets = (
        (None, {
            'fields': ('name', 'emission')
        }),
    )
    search_fields = ['name', 'emission']
    # list_filter = []


class CalculationInline(admin.TabularInline):
    model = Calculation


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [CalculationInline]


class DefaultAmountsInline(admin.TabularInline):
    model = DefaultAmounts


@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    inlines = [DefaultAmountsInline]

