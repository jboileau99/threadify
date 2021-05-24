def reverse(astring):
    revStr = ""
    i = len(astring)-1 
    while i >= 0:
        revStr = revStr + astring[i]
        i = i - 1
    return revStr

print(reverse('quiz 3'))