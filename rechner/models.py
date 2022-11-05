from django.db import models
from django.utils.translation import gettext_lazy as _


## Create your models here.


# Category
class Category(models.Model):
    # Name of category
    name = models.CharField(max_length=100, unique=True)

    # fix plural
    class Meta:
        verbose_name_plural = "Categories"

    # Representation
    def __str__(self):
        return self.name


class Source(models.Model):
    # Name of Source
    name = models.CharField(max_length=100)

    # Author
    author =  models.CharField(max_length=100, blank=True)

    # trusted
    trust =  models.CharField(max_length=50, blank=True)

    # URL
    url =  models.URLField(max_length=500, blank=True)

    # Year
    year =  models.CharField(max_length=50, blank=True)

    # Explanation
    expl = models.CharField(max_length=2000, blank=True)

    # Representation
    def __str__(self):
        return self.name


class EmissionFactor(models.Model):

    # name
    name = models.CharField(max_length=100, unique=True)

    # Factor
    value = models.DecimalField(max_digits=13, decimal_places=7)

    # unit
    unit = models.CharField(max_length=100, blank=True)

    # description
    info = models.CharField(max_length=1000, blank=True)

    # Source
    source = models.ManyToManyField(Source, blank=True)

    # fix plural
    class Meta:
        verbose_name = "Emission Factor"

    # Representation
    def __str__(self):
        return self.name


# emission data
class Emission(models.Model):
    # Name of product
    name = models.CharField(max_length=50, unique=True)

    # Emission in kg per amount
    value = models.DecimalField(max_digits=10, decimal_places=5)

    # unit (kg per what? Should be identical to related Question.unit)
    unit = models.CharField(max_length=20, blank=True)

    # source
    source = models.ManyToManyField(Source, blank=True)

    # EmissionFactor
    factor = models.ManyToManyField(EmissionFactor, blank=True)

    # Explanation
    explanation = models.CharField(max_length=1000, blank=True)

    # Representation
    def __str__(self):
        return self.name



# Question
class Question(models.Model):
    # short name
    name = models.CharField(max_length=100)

    # Text of question
    question_text = models.CharField(max_length=200)

    # Infotext
    info_text = models.CharField(max_length=1000, default="", blank=True)

    # Link to category
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, to_field='name',
                                 default='Sonstige')

    # Unit
    unit = models.CharField(max_length=20, blank=True)

    # Representation
    def __str__(self):
        return self.name

# Templates for Event Types
class EventTemplate(models.Model):
    # Name of event type
    name = models.CharField(max_length=100, unique=True)

    # number of participants
    participants = models.IntegerField(default=20)

    # Short name of event type for url display
    shorty = models.CharField(max_length=15, unique=True, verbose_name=('short'))

    # fix name
    class Meta:
        verbose_name = "Event Template"

    # Representation
    def __str__(self):
        return self.name


# Defaultwerte
class DefaultAmount(models.Model):
    # Link to question
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=('Frage'))

    # Link to template
    template = models.ForeignKey(EventTemplate, on_delete=models.CASCADE)

    # Default value
    value = models.DecimalField(max_digits=10, decimal_places=3, verbose_name=('Default Wert'), blank=True, null=True)

    # Scale with number of people?
    scale = models.BooleanField(default=True, verbose_name=('·#TN'))

    # major aspect?
    important = models.BooleanField(default=True, verbose_name=('Wichtig'))

    # Representation
    def __str__(self):
        return f"Default für {self.question.name} in {self.template.name}"

class CalculationFactor(models.Model):
    # Link to question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # Link to emission
    emission = models.ForeignKey(Emission, on_delete=models.CASCADE)

    # calculation factor
    factor = models.DecimalField(max_digits=10, decimal_places=3, default=1)

    # fixed or multiplied by user input
    fixed = models.BooleanField(default=False)

    # per participant or not
    # pro_TN = models.BooleanField(default=False)

    # explanation
    expl =  models.CharField(max_length=100, blank=True)


    # class Meta:
    #     ordering = ('emission.name',)

    # Representation
    def __str__(self):
        return f"Faktor für {self.emission.name} in {self.question.name}"

class Advice(models.Model):

    # Link to chosen Question
    user_q = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="user_question")


    # Link to suggested Question
    suggested_q = models.ForeignKey(Question, on_delete=models.CASCADE, blank=True, null=True, related_name="suggested_question")

    # suggested reduction factor
    suggested_f = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    # text for name
    text = models.CharField(max_length=200, blank=True, verbose_name="Description")

    # info
    info = models.CharField(max_length=200, blank=True)

    # source
    source = models.ManyToManyField(Source, blank=True)

    # fix plural
    class Meta:
        verbose_name_plural = "Advice"

    # Representation
    def __str__(self):
        if self.suggested_q is not None:
            temp_name = f"Klimatipp für {self.user_q} → {self.suggested_q}"
        else:
            temp_name = f"Klimatipp für {self.user_q}"
        return temp_name

class Stats(models.Model):

    name  =  models.CharField(max_length=100, unique=True)
    count = models.IntegerField(default=0)

    # fix plural
    class Meta:
        verbose_name_plural = "Stats"

    # Representation
    def __str__(self):
        return f"{self.name}: {self.count}"
