
f = open("w5list.txt")
o = open("w5list.new", "w")

word_list = set()

for w in f:
    word = w.strip().upper()
    word_list.add(word)

for word in word_list:
    o.write(word)
    o.write("\n")

f.close()
o.close()
