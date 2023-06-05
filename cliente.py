# 0 para casilla sin seleccionar
# 1 por casilla ocupada por ti
# 2 para casilla ocupada por otro usuario
# 8 por casilla con mina
import socket
import numpy as np

def imprimir_matriz(matriz: np.ndarray) :
    cadena = "   "
    for j in range(0, matriz.shape[0]+1): # Vertical
        for i in range(0, matriz.shape[0]+1) : # Lateral
            if j == 0:
                if i == 0:
                    print(cadena, end="")
                else:
                    cadena = cadena[:1] + str(i) + cadena[len(str(i))+1:]
                    if i == matriz.shape[0]:
                        print(cadena)
                    else:
                        print(cadena, end="")
                    cadena = "   "
            else:
                if i == 0:
                    cadena = cadena[:0] + str(j) + cadena[len(str(j)):]
                    print(cadena, end="")
                    cadena = "   "
                else:
                    cadena = cadena[:1] + matriz[j-1][i-1] + cadena[2:]
                    if i == matriz.shape[0]:
                        print(cadena)
                    else:
                        print(cadena, end="")
                    cadena = "   "


# ----------------------Main---------------------

# print("Inserta la direccion ip del servidor")
HOST = "127.0.0.1"
PORT = 54321 
buffer_size = 1024
dificultad = 0 

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    data = client_socket.recv(buffer_size).decode('utf-8') # bienveidida del servidor
    print(data)
    
    #------------------------------Inicio del juego-------------

    #----------Selecciona dificultad si es el primer cliente-------------
    if data == 'Bienvenido al buscaminas, inserta "F" para facil y "D" para dificil\nPara salir inserta "end"':
        dificultad = input()
        client_socket.sendall(dificultad.encode('utf-8'))

    # Recive si la opcion no es valida o si ya puede jugar
    data = client_socket.recv(buffer_size).decode('utf-8')  # Resive dificultad
    
    while data == "Escoge un simbolo...":
        print(data)
        sym = input()
        client_socket.sendall(bytes(sym,"utf-8"))
        data = client_socket.recv(buffer_size).decode('utf-8')

    dificultad = data.split(",")
    dificultad = dificultad[0]
    # Mientras el mensaje no sea una opcion no valida
    while data == 'Opcion no valida, inserta "F" para facil y "D" para dificil\nPara salir pon "end"':
        print(data, end = "\n\n")
        dificultad = input()
        client_socket.sendall(dificultad.encode('utf-8'))
        data = client_socket.recv(buffer_size).decode('utf-8')
    
    if dificultad == "end" or dificultad == "":
        print("Desconectandose del servidor...")
        client_socket.close()
        exit()

    if dificultad == "F" :
        matriz = np.zeros((9,9), str)
    else :
        matriz = np.zeros((16,16), str)

    for i in range(0, matriz.shape[0]):
        for j in range(0, matriz.shape[0]):
            matriz[i][j] = "-"

    print(data)

    while not (data == "Perdiste" or data == "Ganaste") :
        data = client_socket.recv(buffer_size).decode('utf-8')
        print(data)
        if data != "-" and data != "Perdiste":
            a = data.split(",")
            matriz[int(a[1]) - 1][int(a[2]) - 1] = a[3]
            imprimir_matriz(matriz)
        if data == "Perdiste" or data == "Ganaste":
            print("Juego terminado....")
            break
        if data == "-":
            print("Es tu turno...")
            casilla = input(); 
            posicion = casilla.split(",")
            client_socket.sendall(casilla.encode('utf-8'))
            data = client_socket.recv(buffer_size).decode('utf-8')
            print(data)
            a = data.split(",")
            if data == "Perdiste" or data == "Ganaste":
                matriz[int(posicion[0])-1][int(posicion[1])-1] = "x"
                imprimir_matriz(matriz)
                print("\n" + data)
            elif data == "Casilla ocupada":
                matriz[int(posicion[0])-1][int(posicion[1])-1] = "O"
                imprimir_matriz(matriz)
                print("\nCasilla ocupada")
            elif a[0] == "Bien" : 
                matriz[int(a[1]) - 1][int(a[2]) - 1] = a[3]
                imprimir_matriz(matriz)