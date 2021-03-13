from django.db import models

## Create your models here.

    
# Category
class Category(models.Model):
    
    # Name of category
    name = models.CharField(max_length=100, unique=True)
    
    # Representation
    def __str__(self):
        return self.name
    
    
# Product
class Product(models.Model):
    
    # Name of product
    name = models.CharField(max_length=50, unique=True)

    # Representation
    def __str__(self):
        return self.name
    
# Question 
class Question(models.Model):
    
    # Text of question
    question_text = models.CharField(max_length=200)
    
    # Link to category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field='name', default='Unsortiert') # wollen wir wirklich, dass Fragen gelöscht werden, wenn wir die Kategorie löschen?
    
    # Link to products
    products = models.ManyToManyField(Product)
    
    # Calculation as string. Should be executable using eval(). Eg: "self.products[0]*answer1.amount*Emission5.value"
    calc_co2 = models.CharField(max_length=200)
    
    # Representation
    def __str__(self):
        return self.question_text
    
# Templates for Event Types
class EventTemplate(models.Model):
    
    # Name of event type
    name = models.CharField(max_length=100, unique=True)

    # Link to questions
    questions = models.ManyToManyField(Question)

    # Representation
    def __str__(self):
        return self.name
    
class DefaultAmounts(models.Model):

    # Link to question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Link to template
    template = models.ForeignKey(EventTemplate, on_delete=models.CASCADE)

    # Representation
    def __str__(self):
        return f"default for {self.question.name} in {self.template.name}"
    
