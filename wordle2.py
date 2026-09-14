import re
import random
from collections import Counter

from w5_freq import frequency_map

WORD_LIST_PATH = "wordlists/w5list.new"
# Shorter words, used to spot plurals. Deliberately NOT XwiWordList: it is a
# crossword answer list full of questionable entries (the reason solver.py
# needs its dump command), and its junk stems flag real words as plurals --
# PRESS via "PRES", GRASS via "GRAS", CHAOS via "CHAO", FLOSS via "FLOS".
# Losing a real answer costs far more than missing a plural, so use the clean
# list and close the gap by hand below.
STEM_SOURCES = ("wordlists/words.txt",)

# Four-letter words words.txt lacks, found by auditing what slipped through.
EXTRA_STEMS = {
    "BLOG", "CARB", "CELT", "CHIB", "COMM", "HICK", "JEAN", "LAKH",
    "MAKI", "PESO", "STAT", "TACO", "TAEL", "VIBE",
}

# Plurals with no regular stem to detect.
IRREGULAR_PLURALS = {"ELVES", "WIVES"}
TOP_N_OPENERS = 20

# The NYT has never used a vulgar word or a slur as an answer, so these are
# never worth spending a guess on.
PROFANITY = {
    "ARSED", "ARSES", "BALLS", "BITCH", "BONER", "BOOBS", "CHINK", "CLITS",
    "COCKS", "CRAPS", "CUNTS", "DICKS", "DILDO", "DYKES", "FARTS", "FUCKS",
    "HOMOS", "HONKY", "HORNY", "JIZZM", "KIKES", "NEGRO", "NIGGA", "PENIS",
    "PISSY", "POOPS", "PORNO", "PRICK", "PUBIC", "PUSSY", "QUEER", "RAPED",
    "SEMEN", "SHITE", "SHITS", "SKANK", "SLAGS", "SLUTS", "SPICS", "SQUAW",
    "TITTY", "TURDS", "TWATS", "WANKS", "WHORE",
}

# Nor a proper noun. No word list here preserves capitalisation, so there is
# no signal to detect these automatically -- they have to be named. Only words
# with no everyday lowercase sense are listed: HENRY (the SI unit), JIMMY and
# HARRY (verbs), TERRY (cloth), BAKER, MASON and PIPER (trades), CHINA
# (porcelain), DRAKE (a duck), HOMER (a home run), GABLE (a roof), BELLE,
# PATSY, TEDDY, SONNY, STEIN, BOWIE, ROWAN, TWAIN, MOLLY, SANDY, RANDY and
# the Greek letters all stay, because the NYT could legitimately use them.
PROPER_NOUNS = {
    # given names
    "AGGIE", "ARIEL", "BAMBI", "BARRY", "BENNY", "BETTY", "BOBBY", "BRENT",
    "BRITT", "BUFFY", "BUNTY", "CLINT", "COLIN", "COREY", "CRAIG", "DANNY",
    "DARCY", "DENIS", "DIANE", "DONNA", "DONNY", "DORIS", "ERICA", "FLEUR",
    "GEMMA", "GINNY", "GRIFF", "HAKIM", "JACKY", "JENNY", "JERRY", "JESSE",
    "KELLY", "KERRY", "KYLIE", "LACEY", "LAURA", "LINDY", "LOUIE", "MADGE",
    "MALIK", "MAMIE", "MARIA", "MICKY", "MIRZA", "MITCH", "MOIRA", "MONTY",
    "NANCY", "NELLY", "NORMA", "OZZIE", "PAOLO", "PEDRO", "PEGGY", "PERRY",
    "PETAR", "PILAR", "POLLY", "RAINE", "RAYNE", "RILEY", "RISHI", "SAMMY",
    "SAYID", "SYBIL", "TAMMY", "TOMMY", "TYLER", "WALDO", "WALLY", "WILLY",
    # surnames
    "ABBAS", "ALINE", "AYRES", "BIGGS", "BROCK", "BUNDY", "BURKE", "CHANG",
    "CHING", "CLARY",
    "COHEN", "COLBY", "CUDDY", "EMMET", "FITCH", "FOYLE", "GILLY", "GRAFF",
    "HANKS", "HOGAN", "HORST", "JAFFA", "JONES", "KIRBY", "KONDO", "KRANG",
    "LEARY", "LEONE", "LEWIS", "LIANG", "LOTTE", "LOWRY", "MASSA", "MAVIS",
    "MERLE", "MILOS",
    "MORSE", "NANCE", "PACEY", "PLATT", "POTTS", "PRATT", "RANCE", "REDDY",
    "RIGGS",
    "RUBIN", "SIKES", "SILVA", "SLADE", "SLOAN", "STARR", "SYKES", "WEBER",
    "YATES", "ZORRO",
    # places
    "ALAMO", "CAPRI", "CHICO", "CONGO", "COSTA", "DELOS", "DEVON", "DIXIE",
    "DOVER", "GENOA", "INDIA", "JAPAN", "MINOS", "PARIS", "PARMA", "RHINE",
    "SANTO", "SEINE", "SODOM", "SPAIN", "TEXAS", "VEGAS", "WALES",
    # religious and mythological figures
    "JESUS", "JUDAS", "MOSES", "PLUTO", "TORAH",
    # brands and trademarks
    "CHEVY", "CISCO", "HONDA", "OUIJA", "PEPSI", "TASER",
}


def _load_stems():
    """Three- and four-letter words, keyed by length, for plural detection."""
    stems = {3: set(), 4: set()}
    for source in STEM_SOURCES:
        try:
            with open(source, errors="ignore") as f:
                for line in f:
                    word = line.strip().split(";")[0].upper() # tolerate WORD;score lines
                    if len(word) in stems and word.isalpha():
                        stems[len(word)].add(word)
        except FileNotFoundError:
            continue # a missing source just means weaker detection, not a crash
    stems[4] |= EXTRA_STEMS
    return stems


STEMS = _load_stems()


def is_plural(word):
    """True if word is the plural of a shorter word -- the NYT never uses those.

    Only endings are checked, so words that merely end in S survive: FOCUS,
    BONUS, VIRUS and AEGIS all keep their place because FOCU, BONU, VIRU and
    AEGI are not words.
    """
    if word.endswith("IES") and (word[:-3] + "Y") in STEMS[3]:
        return True # CRIES <- CRY
    if word.endswith("ES") and word[:-2] in STEMS[3]:
        return True # BOXES <- BOX
    if word.endswith("S") and word[:-1] in STEMS[4]:
        return True # TRIPS <- TRIP
    return word in IRREGULAR_PLURALS


def is_playable(word):
    """Could the NYT plausibly use this as an answer?"""
    if word in PROFANITY or word in PROPER_NOUNS:
        return False
    return not is_plural(word)


includes = []
excludes = []
misplaced = {}
patterns = []
# initial guesses (cares, plus a diverse random)

# ask initial pattern  UPPER = Correct letter in position, lower = letter, but wrong position, . = unknown
guess = ' '
pattern = ''

def coverage_scores(word_list, known=()):
    """How many still-useful letters each word covers, over the given pool.

    Letter counts come from the pool itself, so a word scores highly when it
    tests letters that many remaining candidates share -- that is what splits
    the field. Letters already pinned down carry no information and are
    skipped.
    """
    known = set(known)
    letter_counts = Counter()
    for word in word_list:
        letter_counts.update(set(word) - known)
    return {w: sum(letter_counts[c] for c in set(w) - known) for w in word_list}


def opener_pool():
    """Words worth opening with: distinct letters, real frequency, NYT-plausible."""
    pool = []
    with open(WORD_LIST_PATH) as f:
        for line in f:
            word = line.strip()
            if len(word) != len(set(word)):
                continue # repeated letters waste a slot
            if frequency_map.get(word, 0) <= 1:
                continue # 1 is w5_freq's "no data" sentinel, not a ranking
            if not is_playable(word):
                continue
            pool.append(word)
    return pool


def initial_guess():
    """Rank every opener by letter coverage, then offer a few of the best.

    Ranking the whole pool matters: sampling five at random and taking the
    best of those threw away the other 2600-odd words, and ranking by word
    frequency picked common-but-uninformative openers like RIGHT and ABOUT.
    """
    pool = opener_pool()
    if not pool:
        return {}

    cover = coverage_scores(pool)
    ranked = sorted(pool, key=lambda w: (cover[w], frequency_map[w]), reverse=True)
    top = ranked[:TOP_N_OPENERS]

    guess_list = random.sample(top, min(5, len(top)))
    ranked_guesses = {k: (cover[k], frequency_map[k]) for k in guess_list}

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

def score(word_list, known=()):
    """Rank candidates by coverage of unknown letters, tie-broken by frequency.

    Coverage picks the guess that eliminates the most remaining candidates;
    frequency breaks ties toward words actually worth guessing. Returned as
    (coverage, frequency) tuples so max() orders on both.
    """
    cover = coverage_scores(word_list, known)
    return {k: (cover[k], frequency_map[k]) for k in word_list if k in frequency_map}


first_guess = initial_guess()
# Pick at random among the offered openers rather than always taking the best,
# so the game varies instead of opening RAISE every time. They are all drawn
# from the top TOP_N_OPENERS by coverage, so any of them is a strong start.
# An empty dict just means the prompt has no default.
recommended = random.choice(list(first_guess)) if first_guess else ''

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
    # the next lowest genuine score is 159. Drop those, and anything the NYT
    # would never use as an answer, so they are neither listed nor recommended.
    final_list = [x for x in candidate_list
                  if frequency_map.get(x, 0) > 1 and is_playable(x)]
#    print(candidate_list)
    if final_list == []:
        # Everything left was a sentinel word; fall back rather than show nothing.
        final_list = candidate_list
#    print(misplaced)
#    print(excludes)
    #print(len(candidate_list))
    # Letters already confirmed or ruled out tell us nothing further.
    final_options = score(final_list, known=set(includes) | set(excludes))
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
