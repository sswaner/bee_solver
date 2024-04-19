import re
import random

from w5_freq import frequency_map


includes = []
excludes = []
misplaced = {}
patterns = []
# initial guesses (cares, plus a diverse random)

# ask initial pattern  UPPER = Correct letter in position, lower = letter, but wrong position, . = unknown
guess = ' '
pattern = ''

def initial_guess():
    seeds =[random.randrange(1, 12794) for x in range(5)]
    f = open("wordlists/w5list.new")
    guess_list = []
    c = 1
    for w in f:
        if c in seeds:
            if len(w.strip()) == len(set(w.strip())):
                guess_list.append(w.strip())
        c+=1
    ranked_guesses = {}

    for k in guess_list:
        if k in frequency_map:
            ranked_guesses[k] = frequency_map[k]
    
    print(guess_list)
    print(ranked_guesses)
    return ranked_guesses

def evaluate(guess, pattern):
    for l in guess:
        if l.upper() in pattern.upper():
            includes.append(l.upper())
        else:
            excludes.append(l.upper())

#    for l in pattern:
#        if l == '.':
#            continue
#        if not l.isupper():
#            position = pattern.index(l)
#            if l.upper() in misplaced:
#                misplaced[l.upper()].append(position)
#            else:
#                misplaced[l.upper()] = [position]

    for i in range(5):
        if not pattern[i].isupper():
            l = guess[i]
            if l.upper() in misplaced:
                misplaced[l.upper()].append(i)
            else:
                misplaced[l.upper()] = [i]

    pattern_new = ''
    for l in pattern:
        if l.islower():
            pattern_new += '.'
        else:
            pattern_new += l
    if pattern_new not in patterns:
        patterns.append(pattern_new)
    pattern = pattern_new
    return pattern_new

def candidates(includes, excludes, misplaced, pattern):
    #    print("opening file")
    patterns = [pattern]
    f = open("wordlists/w5list.new")
    matches = []
    match = False
    c = 0
    for w in f:
        
        word = w.strip()
        
#        print(word)
        if len(word) != len(pattern):
            #print("incorrect length")
            continue
        if re.match(pattern, word):
            #print(pattern, word)
            #print("pattern match")
            match = True
        else:
            #print(pattern, word)
            #print("no match")
            continue
        for l in includes:
            if l not in word:
#                print("missing include")
                match = False
                continue

        for l in excludes:
            if l in word:
                match = False
        
        for k in misplaced:
            if k in word:
                for i in misplaced[k]:
                    if word[i] == k:
#                        print("misplaced", k, word)
                        match = False
                        continue


        if match:
            print("appending ", word)
            matches.append(word)
#        c += 1
 #       if c> 5: break
 #       print('-' * 20)
    return matches

def score(word_list):
    ranked_list = {}

    for k in word_list:
        if k in frequency_map:
            ranked_list[k] = frequency_map[k]

    return ranked_list

first_guess = initial_guess()
recommended =  max(first_guess, key= lambda x: first_guess[x])

#game = random.randrange(0, 2200)

while guess != pattern:
    guess = input("Enter your guess [{0}]: ".format(recommended))
    if guess.lower() == "exit":
        exit()
    if guess == '':
        guess = recommended
    
    pattern = input("Enter current pattern: " )
    if pattern.lower() == "exit":
        exit()
    pattern = evaluate(guess, pattern)
#    print(includes)
#    print(excludes)
#    print("misplaced")
#    print(misplaced)
#    print("Pattern")
#    print(pattern)
    candidate_list = candidates(includes, excludes, misplaced, pattern)
    final_list = candidate_list
#    final_list = [x for x in candidate_list if len(x) == len(set(x))]
#    print(candidate_list)
    if final_list == []:
        final_list = candidate_list
#    print(misplaced)
#    print(excludes)
    #print(len(candidate_list))
    final_options = score(final_list)
    print(final_options)
    recommended = max(final_options, key= lambda x: final_options[x])
    print("Candidate Count: " + str(len(final_list)))
    print(recommended)
    print('-' * 40)

print("Good Job")

# evaluate pattern versus guess 
# loop until pattern is complete

# ask initial pattern

# suggest next guess

# confirm guess

# 
