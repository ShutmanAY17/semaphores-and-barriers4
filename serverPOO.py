# 1 es para casillas que tienen bombas
# 2 es para las casillas ocupadas por usuarios
# 0 es para las casillas que no tienen nada
import socket
import random
import threading
import numpy as np

# --------------------Funciones para el Busca minas--------------------------------
class Tablero:

    def __init__(self):
        self.dificultad: str
        self.size: int
        self.minas: int
        self.count_open: int
        self.matriz: np.ndarray
        self.terminado = False
    
    def setmatriz(self):    
        if self.dificultad == "F" :
            self.size = 9
            self.minas = 10
        elif self.dificultad == "D" :
            self.size = 16
            self.minas = 40
        else:
            return False
        self.count_open = 0
        self.matriz = np.zeros((self.size,self.size), str)
        
        count = 1
        while count <= self.minas :
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)

            if self.matriz[x][y] == "" :
                self.matriz[x][y] = "1"
                count = count + 1

        return True
    
    def tirada(self, casilla: str, sym: str):
        posicion = casilla.split(",")
        if self.matriz[int(posicion[0])-1][int(posicion[1])-1] == "":
            self.matriz[int(posicion[0])-1][int(posicion[1])-1] = sym
            self.count_open += 1
            print("Bien")
            return "Bien"
        elif self.matriz[int(posicion[0])-1][int(posicion[1])-1] == "1":
            print("Perdiste")
            self.terminado == True
            return "Perdiste"
        else: #self.matriz[int(posicion[0])-1][int(posicion[1])-1] != "":
            print("Casilla ocupada")
            return "Casilla ocupada"
        
# ------------------------------------------------------------------------------------------------------
class Conexion:
    def _init_(self):
        self.client_conn: socket.socket
        self.hilo: threading.Thread
        self.simbolo: str


# --------------------------Funciones del servidor------------------------------------------------------
class Servidor:

    def __init__(self):
        self.server_socket: socket.socket
        self.tablero: Tablero
        self.conexiones: list[Conexion] = []
        self.barrier = threading.Barrier(3)
        self.semaforo = threading.Semaphore(1)
        self.turno = 0

    def init_game(self, num_conn: int):
        self.tablero = Tablero()
        data = self.conexiones[num_conn].client_conn.recv(buffer_size).decode('utf-8')  #Mensaje con la dificultad
        self.tablero.dificultad = data
        dif_is_valid = self.tablero.setmatriz()
        while not dif_is_valid and not (data == "end" or data == ""):
            self.conexiones[num_conn].client_conn.sendall(bytes('Opcion no valida, inserta "F" para facil y ' 
            + '"D" para dificil\nPara salir pon "end"', 'utf-8'))
            data = self.conexiones[num_conn].client_conn.recv(buffer_size).decode('utf-8')
            self.tablero.dificultad = data
            dif_is_valid = self.tablero.setmatriz()
        
        if data == "end" or data == "":
            print("\nDesconectandose del cliente...")
            return False
        print(self.tablero.matriz)
        
        
    def jugar(self, num_conn: int):
        # Implementar aqui una barrera hasta que halla una matriz
        self.barrier.wait()
        self.conexiones[num_conn].client_conn.sendall(bytes(self.tablero.dificultad 
                                  + ', Mapa creado\nPara seleccionar '
                                  + 'una casilla inserta Fila,Columna\nEjemplo: 6,9', 'utf-8'))
        state_game: str
        while True: 
            while self.turno != num_conn:
                pass

            self.semaforo.acquire()

            if self.tablero.terminado:
                self.semaforo.release()
                break
            
            if self.turno == 2:
                self.turno = 0
            else:
                self.turno += 1
            self.conexiones[num_conn].client_conn.sendall(bytes("-", "utf-8")) #Luz verde para hacer tirada
            data = self.conexiones[num_conn].client_conn.recv(buffer_size).decode('utf-8')
            state_game = self.tablero.tirada(data, self.conexiones[num_conn].simbolo)   
            if state_game == "Perdiste":
                for c in self.conexiones:
                    c.client_conn.sendall(b'Perdiste')
                break
            elif state_game == "Bien":
                for c in self.conexiones:
                    # Bien,6,5,{simbolo}
                    c.client_conn.sendall(bytes('Bien,' + data + "," + self.conexiones[num_conn].simbolo, "utf-8"))
            else:
                self.conexiones[num_conn].client_conn.sendall(b'Casilla ocupada')
            if self.tablero.count_open == self.tablero.minas:
                self.conexiones[num_conn].client_conn.sendall(b'Ganaste')
                print(data)
                self.semaforo.release()
                break
            self.semaforo.release()

    def request_sym(self, num_conn: int): 
        while self.conexiones[num_conn].simbolo == "Sin simbolo":
            self.conexiones[num_conn].client_conn.sendall(bytes("Escoge un simbolo...", "utf-8"))
            data = self.conexiones[num_conn].client_conn.recv(buffer_size).decode('utf-8')
            isn_repeated = True
            for c in self.conexiones:
                if data == c.simbolo:
                    isn_repeated = False
                    break
            if data.__len__() == 1 and isn_repeated:
                self.conexiones[num_conn].simbolo = data
                print(self.conexiones[num_conn].simbolo)
             
    def partida(self, num_conn: int):                 
        if num_conn == 0:
            msg_in_btyes = 'Bienvenido al buscaminas, inserta "F" para facil y "D" para dificil\nPara salir inserta "end"'
            msg_in_btyes = msg_in_btyes.encode('utf-8')  # Transforma de stringa a bytes
            self.conexiones[num_conn].client_conn.sendall(msg_in_btyes) # Bienvenida
            self.init_game(num_conn)
        else:
            msg_in_btyes = 'Bienvenido al buscaminas, otro cliente esta elgiendo dificultad...\n\n'
            msg_in_btyes = msg_in_btyes.encode('utf-8')
            self.conexiones[num_conn].client_conn.sendall(msg_in_btyes) # Bienvenida
        self.request_sym(num_conn)
        self.jugar(num_conn)
        
    def acept_conn(self):
        try:
            while True:
                client_conn, client_addr = self.server_socket.accept()
                conexion = Conexion()
                conexion.client_conn = client_conn
                conexion.simbolo = "Sin simbolo"
                self.conexiones.append(conexion)
                num_conexion = self.conexiones.index(conexion)
                print("Conectado al cliente con la ip", client_addr)
                conexion.hilo = threading.Thread(target=self.partida, args=[num_conexion])
                conexion.hilo.start()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    print("Incerta la ip del servidor")
    HOST = "127.0.0.1" # El hostname o IP del servidor
    PORT = 54321  # El puerto que usa el servidor
    buffer_size = 1024
    listaconexiones = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT)) 
        server_socket.listen(2)
        print("Servidor de Buscaminas activo, esperando peticiones\n")
        servidor = Servidor()
        servidor.server_socket = server_socket
        servidor.acept_conn()
            