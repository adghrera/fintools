from django.db import models


class Ticker(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=30)
    exchange = models.CharField(max_length=15)

    def __str__(self):
        return self.id + " - " + self.name


class Eod(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE)
    day = models.DateField()
    open = models.DecimalField(max_digits=12, decimal_places=2)
    close = models.DecimalField(max_digits=12, decimal_places=2)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.DecimalField(max_digits=16, decimal_places=0)

    def __str__(self):
        return str(self.ticker) + "-" + str(self.day)
