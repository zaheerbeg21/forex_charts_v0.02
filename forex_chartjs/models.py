from django.db import models

# Create your models here.
class Currency(models.Model):
    currency_name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)

    def _str_(self) -> str:
        return self.currency_name


class Interval(models.Model):
    minutes = models.IntegerField()
    description = models.TextField()

    def _str_(self) -> str:
        return str(self.minutes)