# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math

from home_price_calculator import HomeLoan


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def compute_home_price(value, year, growth=3.8):
    newvalue = value * math.pow(1.0+growth/100.0, 2022-year)
    return newvalue

def compute_monthly_payment(price, rate, years, paymentsperyear = 12):
    growth = math.pow(1.0 + rate / n, n * years)
    payment = price * (rate / n) * growth / (growth - 1.0)
    return payment

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(compute_home_price(500, 2012, 4.0) * 1.2)
    # print(compute_monthly_payment(1000000.0, 0.06, 12.0, 30.0))
    hl = HomeLoan(400000.0, 0.07, 30.0, 0.015, 140000.0, 12)
    print(hl.calculate_payment())
    print(hl.real_price())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
