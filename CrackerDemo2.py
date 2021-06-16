import string


def getNext(charlist, increment, max_size, ID, current):
    count = 0
    nxt = ""
    if(current == ""):                                                                     
        return charlist[increment-1+ID]                                                  
    else:
        for i in range(len(current)-1, -1, -1):              
            ind = charlist.index(current[i])
            if count == 0:
                if ind+increment >= len(charlist):
                    nxt = charlist[(ind+increment)%len(charlist)] + nxt
                    increment = 1
                else:
                    count = 1
                    nxt = charlist[ind+increment] + nxt
                    increment = 1
            else:
                nxt = current[i] + nxt
        if count == 0:
            nxt = charlist[0] + nxt
        return nxt                          


chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
offset = 1                                                                                 # Number of Slaves
ID = 0                                                                                     # Id of slave
Max_size = 8      
pswd = "" # Max size of passwordds
for i in range(0, 1000):
    pswd = getNext(chars, offset, Max_size, ID, pswd)                                             # Password list to try on
    print(pswd)

