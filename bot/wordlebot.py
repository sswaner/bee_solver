import re
import random
import json
from datetime import datetime

import requests

from w5_freq import frequency_map



def initial_guess():
    seeds =[random.randrange(1, 12794) for x in range(5)]
    f = open("w5list.new")
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
    
#    print(guess_list)
#    print(ranked_guesses)
    if ranked_guesses == {}:
        return {'cares': 10 }
    return ranked_guesses

def evaluate(guess, pattern, includes, excludes, misplaced, patterns):
#    print("evaluate: ", guess, pattern)
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

    for i in range(4):
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
    return (pattern_new, includes, excludes, misplaced, patterns)

def candidates(includes, excludes, misplaced, pattern):
#    print("opening file")
    patterns = [pattern]
    f = open("w5list.new")
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
 #               print("missing include")
                match = False
                continue

        for l in excludes:
            if l in word:
                match = False
        
        for k in misplaced:
            if k in word:
                for i in misplaced[k]:
                    if word[i] == k:
 #                       print("misplaced", k, word)
                        match = False
                        continue


        if match:
            matches.append(word)

    return matches


def score(word_list):
    ranked_list = {}

    for k in word_list:
        if k in frequency_map:
            ranked_list[k] = frequency_map[k]

    return ranked_list


def play_game():
    includes = []
    excludes = []
    misplaced = {}
    patterns = []
    # initial guesses (cares, plus a diverse random)

    # ask initial pattern  UPPER = Correct letter in position, lower = letter, but wrong position, . = unknown
    guess = ' '
    pattern = ''
    first_guess = initial_guess()
    recommended =  max(first_guess, key= lambda x: first_guess[x])

    game = str(random.randrange(0, 2315))

    data = {"game_id" : game, "game_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "outcome": -1, "rounds_played": 0, 'answer': '', "engine": "simple_random",
            "round1": {},
            "round2": {},
            "round3": {},
            "round4": {},
            "round5": {},
            "round6": {}
            }

    for i in range(1, 7):
        
        foo = requests.get("http://127.0.0.1:8000/{1}/{0}".format(recommended, game))
        results = json.loads(foo.text)
        print(str(i), results)
        pattern = results['result']
        round_id = "round{0}".format(i)
        
        data[round_id] = {'guess': recommended, 'result': pattern}
        data['rounds_played'] = i

        if results['guess'] == results['answer']:
            print("Success in {0} guesses: {1}".format(i, results['answer']))
            data['outcome'] = 1
            data['answer'] = results['answer']
            break
    #    x = input("C00000000000000000000000000000000000000000000000000000000000000ontinue")
    #    data[round_id] = {'guess': recommended, 'result': pattern}
        pattern, included, excluded, misplaced, patterns = evaluate(recommended, pattern, includes, excludes, misplaced, patterns)

        candidate_list = candidates(includes, excludes, misplaced, pattern)

        recommended = random.choice(candidate_list)
    if data['outcome'] == -1:
        data['outcome'] = 0
        data['answer'] = results['answer']
        
    print(data)

    columns = ['game_time', 'game_id', 'answer', 'outcome', 'rounds_played', 'engine']

    output = ''

    for column in columns:
        output += str(data[column]) + ','

    for i in range(1, 7):
        if i <= data['rounds_played']:
            round_id = 'round' + str(i)
            output += data[round_id]['guess'] + ','
            output += data[round_id]['result'] + ','
        else:
            output += ',,'
    print(output)

    f = open("gamelog.csv", "a")
    f.write(output)
    f.write('\n')
    f.close()


if __name__ == '__main__':
    play_game()
