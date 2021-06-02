
f = open("XwiWordList.txt")

r = open("xwi_bee_words.txt", 'w+')

for line in f:
    word = line.strip().split(';')[0]
    score = line.strip().split(';')[1]
    word_set = set(word)

    if len(word) < 4:
        continue
    if len(word_set) > 7:
        continue
    print(word, score, len(word_set))
    r.write(word)
    r.write('\n')



f.close()
r.close()
