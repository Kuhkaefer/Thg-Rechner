from django.contrib import admin
from .models import Category, Emission, Question, EventTemplate, DefaultAmounts, Source

# Register your models here.
admin.site.register(Category)
admin.site.register(Source)


class SourceAdminInline(admin.TabularInline):
    model = Emission.source.through


@admin.register(Emission)
class EmissionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'value', 'source', 'unit')
        }),
    )
    search_fields = ['name', 'value', 'source', 'unit']



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    pass


class DefaultAmountsInline(admin.TabularInline):
    model = DefaultAmounts


@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    inlines = [DefaultAmountsInline]
