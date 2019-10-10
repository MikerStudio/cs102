def encrypt_caesar(plaintext: str) -> str:
    """
    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ''
    for letter in list(plaintext):
        ordl = ord(letter)
        # print(ordl)
        if 65 <= ordl <= 87:
            ciphertext += chr(ordl + 3)
        elif ordl == 88:
            ciphertext += 'A'   # Да-да, костыли, знаю
        elif ordl == 89:
            ciphertext += 'B'
        elif ordl == 90:
            ciphertext += 'C'
        elif 97 <= ordl <= 119:
            ciphertext += chr(ordl + 3)
        elif ordl == 120:
            ciphertext += 'a'   # Да-да, костыли, знаю
        elif ordl == 121:
            ciphertext += 'b'
        elif ordl == 122:
            ciphertext += 'c'
        else:
            ciphertext += letter

    # PUT YOUR CODE HERE
    return ciphertext


def decrypt_caesar(ciphertext: str) -> str:
    """
    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    # PUT YOUR CODE HERE


    plaintext = ''
    for letter in list(ciphertext):
        ordl = ord(letter)
        if 68 <= ordl <= 90:
            plaintext += chr(ordl - 3)
        elif ordl == 67:
            plaintext += 'Z'   # Да-да, костыли, знаю
        elif ordl == 66:
            plaintext += 'Y'
        elif ordl == 65:
            plaintext += 'X'
        elif 100 <= ordl <= 121:
            plaintext += chr(ordl - 3)
        elif ordl == 99:
            plaintext += 'z'   # Да-да, костыли, знаю
        elif ordl == 98:
            plaintext += 'y'
        elif ordl == 97:
            plaintext += 'x'
        else:
            plaintext += letter
    return plaintext