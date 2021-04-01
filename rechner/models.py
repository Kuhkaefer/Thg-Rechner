from django.db import models
from django.utils.translation import gettext_lazy as _

## Create your models here.

    
# Category
class Category(models.Model):
    
    # Name of category
    name = models.CharField(max_length=100, unique=True)
    
    # Representation
    def __str__(self):
        return self.name


class Source(models.Model):
    # Name of Source
    name = models.CharField(max_length=200)

    # Author

    # Year

    
# emission data
class Emission(models.Model):
    
    # Name of product
    name = models.CharField(max_length=50, unique=True)

    # Emission per kg
    emission = models.DecimalField(max_digits=10, decimal_places=5)

    # source
    source = models.ManyToManyField(Source)

    # Representation
    def __str__(self):
        return self.name


# Question 
class Question(models.Model):
    
    # short name
    name = models.CharField(max_length=100)
    
    # Text of question
    question_text = models.CharField(max_length=200)
    
    # Link to category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field='name', default='Unsortiert') # wollen wir wirklich, dass Fragen gelöscht werden, wenn wir die Kategorie löschen?

    # Representation
    def __str__(self):
        return self.question_text


class Calculation(models.Model):
    # Question for which the calculation is
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # Link to emission data
    emission = models.ForeignKey(Emission, on_delete=models.CASCADE)

    # Relation between answer and Emission data (calculation not in models)
    ratio = models.DecimalField(max_digits=10, decimal_places=5)

    # Representation
    def __str__(self):
        return self.question.question_text + " " + self.emission.name


# Templates for Event Types
class EventTemplate(models.Model):
    
    # Name of event type
    name = models.CharField(max_length=100, unique=True)

    # Representation
    def __str__(self):
        return self.name


# Defaultwerte
class DefaultAmounts(models.Model):

    # Link to question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Link to template
    template = models.ForeignKey(EventTemplate, on_delete=models.CASCADE)

    # Default value
    value = models.DecimalField(max_digits=10, decimal_places=5, verbose_name=_('Default Value'))

    # Representation
    def __str__(self):
        return f"default for {self.question.name} in {self.template.name}"
