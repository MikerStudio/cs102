def encrypt_vigenere(plaintext, keyword):
    """
    Encrypts plaintext using a Vigenere cipher.
    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ''
    for index, char in enumerate(plaintext):
        sub = char

        if 65 <= ord(char) <= 122:
            change = ord(keyword[index % len(keyword)])
            if 97 <= ord(char) <= 122:
                change -= 97
            else:
                change -= 65

            symbol = ord(char) + change

            if 97 <= ord(char) <= 122 and symbol > 122:
                symbol -= 26

            elif 65 <= ord(char) <= 90 and symbol > 90:
                symbol -= 26

            sub = chr(symbol)
        ciphertext += sub

    return ciphertext


def decrypt_vigenere(ciphertext, keyword):
    """
    Decrypts a ciphertext using a Vigenere cipher.
    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ''
    for index, char in enumerate(ciphertext):
        sub = char

        if 65 <= ord(char) <= 122:
            change = ord(keyword[index % len(keyword)])
            if 97 <= ord(char) <= 122:
                change -= 97
            else:
                change -= 65

            symbol = ord(char) - change

            if 97 <= ord(char) <= 122 and symbol < 97:
                symbol += 26

            elif 65 <= ord(char) <= 90 and symbol < 65:
                symbol += 26

            sub = chr(symbol)
        plaintext += sub

    return plaintext
