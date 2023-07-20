import re


pattern = input("What Pattern? ")
excludes = input("excludes? ")


f = open("wordlists/w5list.txt")
match = False

for w in f:
    word = w.strip()
    #print(word)
    
    if re.match(pattern, word):
        match = True

    for l in word:
        if l in excludes:
            match = False

    if match:
        print(word)
