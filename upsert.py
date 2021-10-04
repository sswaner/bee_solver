import solver

def upsert():
    word = input("word: ").strip().upper()
    
    

    words = open("words.txt")

    add = True
    for w in words:
        if w.strip().upper() == word:
            add = False
    added = open("added_words.txt")
    for w in added:
        if w.strip().upper() == word:
            add = False
    if add:
        print("adding ", word)
        a = open("added_words.txt", "a+")
        a.write(word.upper())
        a.write("\n")
        a.close()
    else:
        print(word, " already in list")

    words.close()

if __name__ == '__main__':
    while True:
        upsert()
