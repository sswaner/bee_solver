
l  = open("w5list.new")
o = open("w5_freq.py", "w")
o.write("frequency_map = {\n")

f = open("en_5w.txt")


for w in l:
    word = w.strip()
    scored = False    
    print(word)
    for l in f:
        parts = l.split()
        if parts[0] == word.lower():
            print(l)
            scored = True
            o.write("'{0}':{1},\n".format(word.upper(), parts[1]))
            continue
    if not scored:
            o.write("'{0}':{1},\n ".format(word.upper(), 1))
            
    f.seek(0,0)
f.close()
o.write("\n}")
o.close()




