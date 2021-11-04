## Print a list of all combinations of 6 letters where
## no letter is repeated.  
## Example: ABCDEF,...  AFKMXZ, ... UVWXYZ  

def ratchet(inputs):

    letters = [chr(x) for x in range(65, 91)]
    p = set([])# set
    for i in inputs:
        for l in letters:
            if l in i:
                continue
            else:
                x = ''.join(sorted(''.join(set([i ,  l]))))
                p.add(x)
    return p


r = [chr(x) for x in range(65, 91)]
for i in range(5):
    r  = ratchet(r)


print(r)
print(len(r))
