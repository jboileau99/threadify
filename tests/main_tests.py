from threadify import threadify
import random

def factorial(number):
    """Calculates the factorial of a number"""
    factorial = 1
    if number != 0:
        for i in range(1, number + 1):
            factorial = factorial*i
    return factorial

rand_list = random.sample(range(100), 1000)

result = threadify.Threadify(factorial, data=rand_list, max_threads=10)
