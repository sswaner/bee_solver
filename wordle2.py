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
    # Build the pool of usable openers up front rather than sampling line
    # numbers: a good first guess has five distinct letters AND a real
    # frequency. A frequency of 1 is w5_freq's "no data" sentinel, so those
    # words can never be a sensible recommendation.
    pool = []
    fallback_pool = []
    with open("wordlists/w5list.new") as f:
        for w in f:
            word = w.strip()
            if len(word) != len(set(word)):
                continue # repeated letters make for a weak opener
            fallback_pool.append(word)
            if frequency_map.get(word, 0) > 1:
                pool.append(word)

    if not pool:
        pool = fallback_pool # nothing scored; better a weak guess than none
    if not pool:
        return {}

    guess_list = random.sample(pool, min(5, len(pool)))
    ranked_guesses = {k: frequency_map[k] for k in guess_list if k in frequency_map}

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
# initial_guess can come back empty if the word list or frequency map is
# missing; an empty recommendation just means the prompt has no default.
recommended = max(first_guess, key= lambda x: first_guess[x]) if first_guess else ''

#game = random.randrange(0, 2200)

while guess != pattern:
    guess = input("Enter your guess [{0}]: ".format(recommended))
    if guess.lower() == "exit":
        exit()
    if guess == '':
        if recommended == '':
            print("No recommendation available -- please type a guess.")
            continue
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
    # A frequency of 1 is w5_freq's "no real data" sentinel, not a ranking --
    # the next lowest genuine score is 159. Drop those candidates so they are
    # neither listed nor recommended.
    final_list = [x for x in candidate_list if frequency_map.get(x, 0) > 1]
#    print(candidate_list)
    if final_list == []:
        # Everything left was a sentinel word; fall back rather than show nothing.
        final_list = candidate_list
#    print(misplaced)
#    print(excludes)
    #print(len(candidate_list))
    final_options = score(final_list)
    print(final_options)
    if final_options:
        recommended = max(final_options, key= lambda x: final_options[x])
    else:
        # Nothing matched -- usually a typo in the guess or pattern. Drop the
        # default instead of blowing up on max() of an empty sequence.
        recommended = ''
        print("No scored candidates left; check the guess and pattern entered.")
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
