import re

pattern = '.ON....'

f = open("words.txt")
letters = ['E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D', 'G', 'H', 'L', 'X', 'C' 'V', 'N']
match = True

for l in f:
	if len(l.strip()) != len(pattern):
		continue
	for x in l.strip():
		if x not in letters:
			match = False
			
	if re.match(pattern,l.strip().upper()):				
		print(l.strip().upper())