import string
import random


def generate_random_string(length=5, charset=string.ascii_lowercase):
    return ''.join(random.choices(charset, k=length))


def generate_random_string_array(count=5, length=5):
    return [generate_random_string(length=length) for _ in range(count)]
