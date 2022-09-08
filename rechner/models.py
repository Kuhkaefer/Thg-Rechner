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

    # URL

    # Year

    # Explanation
    expl = models.CharField(max_length=2000)

    # Representation
    def __str__(self):
        return self.name


# emission data
class Emission(models.Model):
    # Name of product
    name = models.CharField(max_length=50, unique=True)

    # Emission per kg
    value = models.DecimalField(max_digits=10, decimal_places=5)

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

    # Infotext
    info_text = models.CharField(max_length=1000, default="")

    # Link to category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field='name',
                                 default='Unsortiert')  # wollen wir wirklich, dass Fragen gelöscht werden, wenn wir die Kategorie löschen?

    # Link to emission(s)
    emissions = models.ManyToManyField(Emission)

    # multiply with n_ppl or not
    multiply_by_ppl = models.BooleanField(default=False)

    # Calculate emissions with user input (value)
    def calc(self, value, n_ppl=1):
        emission_sum = 0
        # Loop through related emissions
        for e in emissions:
            # sum up and multiply with user entry
            emission_sum += e.emission * value
        # multply with number of participants
        if self.multiply_by_ppl:
            emission_sum *= n_ppl
        # return result
        return emission_sum

    # Representation
    def __str__(self):
        return self.question_text

# Templates for Event Types
class EventTemplate(models.Model):
    # Name of event type
    name = models.CharField(max_length=100, unique=True)

    # Short name of event type for url display
    shorty = models.CharField(max_length=15, unique=True)

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
    value = models.DecimalField(max_digits=10, decimal_places=5, verbose_name=_('Default Value'), blank=True, null=True)

    # Representation
    def __str__(self):
        return f"default for {self.question.name} in {self.template.name}"
