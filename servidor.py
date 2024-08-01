import socket
import select

HEADER_LENGTH = 1000
IP = "127.0.0.1"
PORT = 1602

servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor_socket.bind((IP, PORT))
servidor_socket.listen()

lista_sockets = [servidor_socket]
clientes = {}

print(f'SERVIDOR EN LINEA {IP}:{PORT}...')

def recibir_mensaje(socket_cliente):
    try:
        mensaje_encabezado = socket_cliente.recv(HEADER_LENGTH)
        if not mensaje_encabezado:
            return False
        
        tamaño_del_mensaje = int(mensaje_encabezado.decode('utf-8').strip())
        return {'encabezado': mensaje_encabezado, 'data': socket_cliente.recv(tamaño_del_mensaje)}
    except:
        return False

while True:
    leer_sockets, _, exception_sockets = select.select(lista_sockets, [], lista_sockets)
    for socket_notificado in leer_sockets:
        if socket_notificado == servidor_socket:
            socket_cliente, direccion_cliente = servidor_socket.accept()
            usuario = recibir_mensaje(socket_cliente)
            if usuario is False:
                continue
            lista_sockets.append(socket_cliente)
            clientes[socket_cliente] = usuario
            print(f'Nueva conexión de {direccion_cliente[0]}:{direccion_cliente[1]} nombre de usuario: {usuario["data"].decode("utf-8")}')
        else:
            mensaje = recibir_mensaje(socket_notificado)
            if mensaje is False:
                print(f'Conexión cerrada de {clientes[socket_notificado]["data"].decode("utf-8")}')
                lista_sockets.remove(socket_notificado)
                del clientes[socket_notificado]
                continue
            
            usuario = clientes[socket_notificado]
            datos_mensaje = mensaje["data"].decode("utf-8")
            
            if datos_mensaje.lower() == "cerrar_sesion":
                print(f'--- {usuario["data"].decode("utf-8")} se ha desconectado ---')
                lista_sockets.remove(socket_notificado)
                del clientes[socket_notificado]
                continue

            print(f'*Mensaje de {usuario["data"].decode("utf-8")}: {datos_mensaje}*')
            for cliente_socket in clientes:
                if cliente_socket != socket_notificado:
                    cliente_socket.send(usuario['encabezado'] + usuario['data'] + mensaje['encabezado'] + mensaje['data'])
    
    for socket_notificado in exception_sockets:
        lista_sockets.remove(socket_notificado)
        del clientes[socket_notificado]
