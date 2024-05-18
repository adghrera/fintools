import math

class HomeLoan(object):

    def __init__(self, price, rate, years, propertyTax, downPayment = 0.0, paymentsPerYear = 12):
        self.price = price
        self.downPayment = downPayment
        self.rate = rate
        self.years = years
        self.propertyTax = propertyTax
        self.paymentsPerYear = paymentsPerYear

    def calculate_payment(self):
        tax = (self.propertyTax * self.price) / self.paymentsPerYear
        realPrice = self.price - self.downPayment
        growth = math.pow(1.0 + self.rate / self.paymentsPerYear, self.paymentsPerYear * self.years)
        payment = tax + realPrice * (self.rate / self.paymentsPerYear) * growth / (growth - 1.0)
        return payment

    def real_price(self):
        return self.downPayment + self.years * self.paymentsPerYear * self.calculate_payment()

