def contains(texto, lista):
    for elemento in lista:
        if elemento.lower() in texto.lower():
            return True
    return False