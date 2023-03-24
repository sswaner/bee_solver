f = open("w5list.new")
o = open("wordlist.py", "w")

o.write("'words_list' = [\n")

for w in f:
    word = w.strip()
    o.write("'" + word + "',\n")




o.write("\n]\n")

o.close()
f.close()
