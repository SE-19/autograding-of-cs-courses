def factorial(num):
    temp = num
    result = 1
    while temp > 0:
        result *= temp
        temp -= 1
    return result