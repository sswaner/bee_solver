from sys import argv
import textwrap
import random

from tabulate import tabulate

f = open("words.txt")
#f = open("XwiWordList.txt")
#o = input("Enter 7 characters: ").upper()
#c = o[0]

#c = "Q" #The center, must have letter
#o = ["Q", 'U', "R", "M", "I", 'E', 'L'] #The other letters

def solve(words, input_string, full = True):
    results = []
    count = 0
    c = input_string[0]
    for word in words:
        w = word.strip().upper()
        match = False
        if len(w) < 4: 
            continue #too short
        if  c in w:
            match = True
            for l in w:
                if l not in input_string:
                    match = False
                    continue
            if match:
                results.append(w)
    # add words
    if full:
        added_word_list = open("added_words.txt")

        added = solve(added_word_list, input_string, False)
        if added:
            for match in added:
                results.append(match)
    #results = results.sort()
#    print("Removing ---------------- ")
    removed_word_list = open('removed_words.txt')
    for word in removed_word_list:
#        print(word)
        if word.strip().upper() in results:
#            print('remove ', word.strip().upper())
            results.remove(word.strip().upper())
#    print("end Removing")
    return sorted(results)

def search(filename, input_string, exact_match = True):
    word = open('./{0}'.format(filename))
    matches = []
    for word in words:
        if exact_match:
            if input_string == word.strip():
                words.close()
                return ([word], True)
        else:
            if input_string in word.strip():
                matches.append(word.strip())
    words.close()
    return (matches, False)

def pangram(words, input_string):
    i = set(input_string)
    results = []
    for word in words:
        w = set(word.strip())
        if w == i:
            results.append(word)
    return results

def score(words, pangrams):
 #   print("pangrams: ", pangrams)
    total_score = 0
    for word in words:
        if len(word) == 4:
            score = 1
        else:
            score = len(word.strip())
        for p in pangrams:
 #           print(p)
            if word == p:
                score += 7
        total_score += score
#        print(word, score, total_score)
    return total_score

def histogram(matches):
    slug_list = {}

    for word in matches:
        slug = word[:1]
        if slug in slug_list:
            slug_list[slug] += 1
        else:
            slug_list[slug] = 1
    
    long_slugs = [k for k,v  in slug_list.items() if v > 3]
    
    #for (k, v) in long_slugs:
    for word in matches:
        if word[:1] in long_slugs:
            slug = word[:2]
            if slug in slug_list:
                slug_list[slug] += 1
            else:
                slug_list[slug] = 1

    return slug_list

def display(pattern, matches, extended_matches = None):

    matches_str = ', '.join(matches)
    table = []
    all_words = textwrap.wrap( ', '.join(matches), 70)
    table.append(["All Words", textwrap.fill(matches_str)])
    table.append(['Count', len(matches)])
    pangrams = pangram(matches, pattern)
    pangrams_text = textwrap.fill(', '.join(pangrams))
    table.append(['Pangrams', pangrams_text])
    table.append(['Histogram', textwrap.fill(str(histogram(matches)))])
    table.append(['Score', score(matches, pangrams)])
    if extended_matches:
        extended_text = textwrap.fill(', '.join(extended_matches))
        table.append(['Extended Matches({0})'.format(len(extended_matches)), extended_text])

    headers = ['Section', 'Results']
    print(tabulate(table, headers, tablefmt="grid"))

def show_menu(pattern=None):
    if not pattern:
        o = input("Enter 7 characters: ").upper()
    
def add(word):
    f = open("added_words.txt", "a+")
    f.write(word.upper())
    f.write("\n")

    f.close()

def remove(word):
    f = open("removed_words.txt", "a+")
    f.write(word.upper())
    f.write("\n")

    f.close()

if __name__ == "__main__":
    #option = show_menu()
    command = 'solve'
    commands = ['solve', 'hint', 'add', 'remove']

    if len(argv) == 2:
        if argv[1] not in commands:
            print("solving for pattern" + argv[1])
            pattern = argv[1]
        else:
            pattern = input("Enter 7 characters: ").upper()
    elif len(argv) == 3:
        command = argv[1]
        pattern = argv[2]
    
    pattern = pattern.upper()

    if command == 'solve':
        matches = solve(f, pattern, True)
        xwords = open('xwi_bee_words.txt')
        extended = [w for w in solve(xwords, pattern, True) if w not in matches]
        display(pattern, matches, extended)
    elif command == 'hint':
        matches = solve(f, pattern, True)
        print("Try: ", random.choice(matches))
    elif command == 'add':
        print('add', pattern)
        add(argv[2].strip())
    elif command == 'remove':
        remove(argv[2].strip())
        print('remove', argv[2].strip())
    else:
        print('no command operation found')
