import socket
import threading
import sys 

HEADER_LENGHT = 10 

IP = "127.0.0.1"
PORT = 1602 

socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect((IP,PORT))
socket_cliente.setblocking(False)
Minombre_usuario = input("INGRESE SU NOMBRE DE USUARIO: ")
nombre_usuario = Minombre_usuario.encode ('utf-8')
encabezado_usuario = f"{len(nombre_usuario):<{HEADER_LENGHT}}".encode('utf-8')
socket_cliente.send(encabezado_usuario + nombre_usuario)
coneccion_activa = True

def recibir_mensajes (): 
    global coneccion_activa 
    while coneccion_activa: 
        try: 
            encabezado_mensaje = socket_cliente.recv(HEADER_LENGHT)
            if not encabezado_mensaje: 
                print("--- CONEXION CERRADA POR EL SERVIDOR ---")
                coneccion_activa = False
                break

            longitud_nombre_usuario = int(encabezado_mensaje.decode('utf-8').strip())

            nombre_usuario = socket_cliente.recv(longitud_nombre_usuario).decode('utf-8')

            encabezado_mensaje = socket_cliente.recv(HEADER_LENGHT)
            if not encabezado_mensaje:
                print(f"--- CONEXION CERRADA POR EL SERVIDOR--- ")
                coneccion_activa = False
                break
            longitud_nombre_usuario = int(encabezado_mensaje.decode('utf-8').strip())
            mensaje = socket_cliente.recv(longitud_nombre_usuario).decode('utf-8')
            print(f"{nombre_usuario} > {mensaje}")
        except IOError as e:
            if e.errno != socket.errno.EAGAIN and e.errno != socket.errno.EWOULDBLOCK: 
                print ('ERROR DE LECTURA:', str(e))
                coneccion_activa = False 
                break
            continue
        except Exception as e: 
            print('Error:', str (e))
            coneccion_activa = False
            break
def enviar_mensajes(): 
    global coneccion_activa
    while coneccion_activa:
        mensaje = input (f'{nombre_usuario} > ')
        if mensaje: 
            mensaje = mensaje.encode('utf-8')
            encabezado_mensaje = f"{len(mensaje):{HEADER_LENGHT}}".encode("utf-8")
            socket_cliente.send(encabezado_mensaje + mensaje )
            if mensaje.decode('utf-8').lower() == "cerrarsesion":
                print ("CERRANDO CESION ")
                coneccion_activa = False
                socket_cliente.close()
                break
recibir_hilo = threading.Thread(target=recibir_mensajes)
enviar_hilo = threading.Thread(target=enviar_mensajes)

recibir_hilo.start()
enviar_hilo.start()

recibir_hilo.join()
enviar_hilo.join()