def our_fun(txt):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    cipher = ''
    
    for i in range(len(txt)):
        if txt[i] not in alphabet:
            cipher += txt[i]
            continue

        alphabet_ind = alphabet.index(txt[i])
        
        cipher += alphabet[((i + 1) + alphabet_ind) % 26]

    return cipher

print(our_fun('benny'))