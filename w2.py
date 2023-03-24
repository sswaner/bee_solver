

guess = ''
pattern = '.....'
includes = set()
excludes = set()
antipatterns = set()

c = 1
while guess != pattern:
    if c == 1:
        print("recommended start: CARES")
    guess = input("What did you guess?: ").upper()
    pattern = input("What is the new pattern?: ").upper()
    
    if pattern == guess: break

    for l in pattern:
        if l != '.':
            includes.add(l)
    new_includes = input("What other letters are included? ({0}) ".format(','.join(sorted(includes)))).upper()
    for l in new_includes:
        includes.add(l)

    for l in guess:
        if l not in includes:
            excludes.add(l)
    new_excludes = input("Are there any new excludes? ({0})".format(','.join(sorted(excludes)))).upper()
    for l in new_excludes:
        excludes.add(l)

    i = 0
    antipattern = ''
    for l in guess:
        if l not in includes:
            antipattern += '.'
            continue
        antipattern += max(l, pattern[i:i+1])
        i += 1

    print("Antipattern: " ,antipattern)


    print("Includes: {0}".format(",".join(includes)))
    print("Excludes: {0}".format(",".join(excludes)))
    c += 1
