import socket
import threading
import sys

HEADER_LENGTH = 1000
IP = "127.0.0.1"
PORT = 1602

socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect((IP, PORT))
socket_cliente.setblocking(False)

mi_nombre_usuario = input("Ingrese su nombre de usuario: ")
nombre_usuario = mi_nombre_usuario.encode('utf-8')
encabezado_usuario = f"{len(nombre_usuario):<{HEADER_LENGTH}}".encode('utf-8')
socket_cliente.send(encabezado_usuario + nombre_usuario)
conexion_activa = True

def recibir_mensajes():
    global conexion_activa
    while conexion_activa:
        try:
            encabezado_mensaje = socket_cliente.recv(HEADER_LENGTH)
            if not encabezado_mensaje:
                print("--- Conexión cerrada por el servidor ---")
                conexion_activa = False
                break

            longitud_nombre_usuario = int(encabezado_mensaje.decode('utf-8').strip())
            nombre_usuario = socket_cliente.recv(longitud_nombre_usuario).decode('utf-8')

            encabezado_mensaje = socket_cliente.recv(HEADER_LENGTH)
            if not encabezado_mensaje:
                print("--- Conexión cerrada por el servidor ---")
                conexion_activa = False
                break

            longitud_mensaje = int(encabezado_mensaje.decode('utf-8').strip())
            mensaje = socket_cliente.recv(longitud_mensaje).decode('utf-8')
            print(f"{nombre_usuario} > {mensaje}")
        except IOError as e:
            if e.errno != socket.errno.EAGAIN and e.errno != socket.errno.EWOULDBLOCK:
                print('Error de lectura:', str(e))
                conexion_activa = False
                break
            continue
        except Exception as e:
            print('Error:', str(e))
            conexion_activa = False
            break

def enviar_mensajes():
    global conexion_activa
    while conexion_activa:
        mensaje = input(f'{mi_nombre_usuario} > ')
        if mensaje:
            mensaje = mensaje.encode('utf-8')
            encabezado_mensaje = f"{len(mensaje):<{HEADER_LENGTH}}".encode('utf-8')
            socket_cliente.send(encabezado_mensaje + mensaje)
            if mensaje.decode('utf-8').lower() == "cerrar_sesion":
                print("Cerrando sesión...")
                conexion_activa = False
                socket_cliente.close()
                break

recibir_hilo = threading.Thread(target=recibir_mensajes)
enviar_hilo = threading.Thread(target=enviar_mensajes)

recibir_hilo.start()
enviar_hilo.start()

recibir_hilo.join()
enviar_hilo.join()
