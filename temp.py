import math
import random

def OTPgenerator():
    string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""

    for c in range(22):
        OTP += string[math.floor(random.randint(0,len(string)-1))]
    return OTP

print(OTPgenerator())