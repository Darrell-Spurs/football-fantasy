ostr = input()
import random, time
str = [c for c in ostr.replace(" ","")]
random.shuffle(str)

old = ostr.find(" ")
while old!=-1:
    print(old)
    ostr =ostr[:old]+"|"+ostr[old+1:]
    print(ostr)
    str.insert(old,"|")
    old = ostr.find(" ")

print("".join(str).replace("|"," "))
