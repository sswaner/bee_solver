f = open("en_50k.txt")
o = open("en_5w.txt" , "w")

for w in f:
    parts = w.strip().split()
    if len(parts[0]) != 5: continue
    else:
        o.write(w)
o.close()
f.close()
