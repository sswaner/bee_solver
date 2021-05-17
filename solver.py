from sys import argv
import textwrap

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
        print(added)
        if added:
            for match in added:
                results.append(match)
    #results = results.sort()
    print("Removing ---------------- ")
    removed_word_list = open('removed_words.txt')
    for word in removed_word_list:
        print(word)
        if word.strip().upper() in results:
            print('remove ', word.strip().upper())
            results.remove(word.strip().upper())
    print("end Removing")
    return sorted(results)


def pangram(words, input_string):
    i = set(input_string)
    results = []
    for word in words:
        w = set(word.strip())
        if w == i:
            results.append(word)
    return results

def score(words, pangrams):
    print("pangrams: ", pangrams)
    total_score = 0
    for word in words:
        if len(word) == 4:
            score = 1
        else:
            score = len(word.strip())
        for p in pangrams:
            print(p)
            if word == p:
                score += 7
        total_score += score
        print(word, score, total_score)
    return total_score

def display(pattern, matches):

    matches_str = ', '.join(matches)
    table = []
    all_words = textwrap.wrap( ', '.join(matches), 70)
    table.append(["All Words", textwrap.fill(matches_str)])
    table.append(['Count', len(matches)])
    pangrams = pangram(matches, pattern)
    pangrams_text = textwrap.fill(', '.join(pangrams))
    table.append(['Pangrams', pangrams_text])

    table.append(['Score', score(matches, pangrams)])

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
    for a in argv:
        print(a)

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
        display(pattern, solve(f, pattern, True))
    elif command == 'hint':
        print('hint', pattern)
    elif command == 'add':
        print('add', pattern)
        add(argv[2].strip())
    elif command == 'remove':
        remove(argv[2].strip())
        print('remove', argv[2].strip())
    else:
        print('no command operation found')
