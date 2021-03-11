from django.db import models

## Create your models here.

    
# Category
class Category(models.Model):
    
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    
# Question 
class Question(models.Model):
    
    question_text = models.CharField(max_length=200)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field='name', default='Unsortiert') # wollen wir wirklich, dass Fragen gelöscht werden, wenn wir die Kategorie löschen?
    
    def __str__(self):
        return self.question_text
    
