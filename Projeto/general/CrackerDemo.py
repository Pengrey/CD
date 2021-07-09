import string
def getPswds(charlist, increment, max_size, ID: int = 0, pswds: str = []):
    if(max_size == 0):                                                                      # Check if we are done in creating paswds
        return [pswds[i] for i in range(ID,len(pswds),increment)]                           # Return subset of paswds that matter for this ID 
    if(len(pswds) == 0):                                                                    # If we are starting to create the list, just copy it from the char array
        pswds = [pswd for pswd in charlist]                                                 #
    else:                                                                                   #
        if(len(pswds) == len(charlist)):                                                    # If we are on our first iteration of another size, we copy from the first list
            pswds.extend([i + pswd for i in charlist for pswd in pswds])                    #
        else:                                                                               # If we are on another iteration we copy from the previous and add it size
            pswds.extend([i + pswd for i in charlist for pswd in pswds[:-len(charlist)]])   #   
    return getPswds(charlist, increment, max_size - 1, ID, pswds)                           # Call function for another size
    


chars = string.ascii_uppercase + string.ascii_lowercase + string.digits                     # Chars used to make the password
offset = 4                                                                                  # Number of Slaves
ID = 3                                                                                      # Id of slave
Max_size = 8                                                                                # Max size of passwordds
pswds = getPswds(chars, offset, Max_size, ID)                                               # Password list to try on

for pswd in pswds[:2*len(chars)]:
    print(pswd)
