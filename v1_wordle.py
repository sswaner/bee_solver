import re
import random

def scan(pattern, included, excluded, guesses):
    f = open("wordlists/w5list.new")
    matches = []
    match = False
    for w in f:
        word = w.strip()
        if len(word) != len(pattern):
            continue
        if re.match(pattern, word):
            match = True
        for l in included:
            if l not in word:
                match = False
        for l in excluded:
            if l in word:
                match = False
        if match:
            
            for guess in guesses:
                g_pattern = guess
                for l in excluded:
                    g_pattern = g_pattern.replace(l, '.')
                
                m =  re.match(g_pattern, word)
                print(word, g_pattern, m)
                if m:
                    match = False
                else:
                    match = True
                    break
        if match:
            matches.append(word)
    return matches

included = []
excluded = []
guesses = []

while True:
    pattern = input("Pattern: ").upper()
    include_list = ','.join(included)
    new_include = input("Included Letters [{0}]: ".format(include_list)).upper()
    for l in new_include:
        included.append(l)

    exclude_list = ','.join(excluded)
    new_exclude = input("Excluded Letters [{0}]: ".format(exclude_list)).upper()
    for l in new_exclude:
        excluded.append(l)
    matches = scan(pattern, included, excluded, guesses)
    recommends = [x for x in matches if len(set(x)) ==5]
    print(','.join(recommends))
    if len(matches) > 0:
        print("Recommended Guess: ", random.choice(recommends))
    else:
        print("Out of recommendations")
    guess = input("What did you guess? ").upper()
    guesses.append(guess)
