import string
def getPswds(charlist, increment, pswd: str = "a"):
    limit = len(charlist)
    for k in range(increment):
        remain = 1
        new_pswd = list(pswd)
        for i in range(len(new_pswd)-1,-1,-1):
            if (charlist.index(new_pswd[i]) + remain) >= limit:
                if(i != 0):
                    new_pswd[i] = charlist[0]
                    remain = 1
                else:
                    new_pswd[i] = charlist[0]
                    new_pswd.insert(0, charlist[0])
                    remain = 0
            else:
                new_pswd[i] = charlist[charlist.index(new_pswd[i]) + remain]
                remain = 0
            if remain == 0: break
        pswd = "".join(new_pswd)
    return pswd
    


chars = string.ascii_uppercase + string.ascii_lowercase + string.digits                     # Chars used to make the password
offset = 1                                                                                  # Number of Slaves
pswd = "9"                                                                                  # Previous password
pswd = getPswds(chars, offset, pswd)                                                        # Next password to try it on

for i in range(0,197):
    pswd = getPswds(chars, offset, pswd)
    print(pswd)