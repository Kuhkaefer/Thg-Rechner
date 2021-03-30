from django.db import models

## Create your models here.

    
# Category
class Category(models.Model):
    
    # Name of category
    name = models.CharField(max_length=100, unique=True)
    
    # Representation
    def __str__(self):
        return self.name
    
    
# emission data
class Emission(models.Model):
    
    # Name of product
    name = models.CharField(max_length=50, unique=True)

    # Emission per kg
    emission = models.DecimalField()

    # source
    source = models.CharField(max_length=200, unique=True)

    # Representation
    def __str__(self):
        return self.name
    
# Question 
class Question(models.Model):
    
    # Text of question
    question_text = models.CharField(max_length=200)
    
    # Link to category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field='name', default='Unsortiert') # wollen wir wirklich, dass Fragen gelöscht werden, wenn wir die Kategorie löschen?
    
    # Link to emission data / separate model for calculation relation (with question, product, calc_co2) if we need multiple emission sources somewhere
    product = models.ForeignKey(Emission, on_delete=models.CASCADE)
    
    # Relation between answer and Emission data (calculation not in models)
    calc_co2 = models.DecimalField(min_value=0)
    
    # Representation
    def __str__(self):
        return self.question_text
    
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
    value = models.DecimalField(min_value=0)

    # Representation
    def __str__(self):
        return f"default for {self.question.name} in {self.template.name}"
    
class Source(models.Model):
    
    # Name of Source
    name = models.CharField(max_length=200)
    
    # Author

    # Year
