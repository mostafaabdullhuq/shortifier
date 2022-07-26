from string import ascii_lowercase,ascii_uppercase, digits, punctuation
from random import choice

lettersList = []
for i in [ascii_lowercase, digits, ascii_uppercase]:
    for char in i:
        lettersList.append(char)


def generateApikey():
    apiKey = ''
    for i in range(40):
        apiKey+=(choice(lettersList))
    return apiKey