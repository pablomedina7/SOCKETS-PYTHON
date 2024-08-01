import socket           #RED
import select           #ESPERA DE MULTIPLES FLUJOS DE ENTRADA Y SALIDA

HEADER_LENGTH = 1000
IP = "127.0.0.1"
PORT = 1602

servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     #Ipc4 y TCP
servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #Para reutilizar la direccion
servidor_socket.bind((IP, PORT))
servidor_socket.listen()

lista_sockets = [servidor_socket]
clientes = {}       #diccionario para almacenar a los clientes en linea 

print(f'SERVIDOR EN LINEA {IP}:{PORT}...') #informacion del server

def recibir_mensaje(socket_cliente):
    try:
        mensaje_encabezado = socket_cliente.recv(HEADER_LENGTH) #recibir el header dek msj 
        if not mensaje_encabezado:   #en el caso de no recibir nada el cliente está desconectado 
            return False
        
        tamaño_del_mensaje = int(mensaje_encabezado.decode('utf-8').strip())  #decodifica y obtiene el tam
        return {'encabezado': mensaje_encabezado, 'data': socket_cliente.recv(tamaño_del_mensaje)} #decod y obtiene el tamaño del mensaje
    except:     #Ante cualquier excep es f
        return False

while True:
    leer_sockets, _, exception_sockets = select.select(lista_sockets, [], lista_sockets)   #para esperar que los sockets esten listos para ser leidos o tengan excepciones
    for socket_notificado in leer_sockets:     #itera sobre los sockets que esten listos para ser leidos 
        if socket_notificado == servidor_socket:        #Si esta lsito, acepta una nueva conexion
            socket_cliente, direccion_cliente = servidor_socket.accept()    #acepta la conexion 
            usuario = recibir_mensaje(socket_cliente)           #se añade a la lista 
            if usuario is False:
                continue
            lista_sockets.append(socket_cliente) #se añade a la lista 
            clientes[socket_cliente] = usuario
            print(f'Nueva conexión de {direccion_cliente[0]}:{direccion_cliente[1]} nombre de usuario: {usuario["data"].decode("utf-8")}')
        
        else:
            mensaje = recibir_mensaje(socket_notificado)        #recibir msj 
            
            if mensaje is False:
                print(f'Conexión cerrada de {clientes[socket_notificado]["data"].decode("utf-8")}')  #imprime la información de desconexion 
                lista_sockets.remove(socket_notificado)         #elimina del diccionario de usuarios activos 
                del clientes[socket_notificado]
                continue
            
            usuario = clientes[socket_notificado]
            datos_mensaje = mensaje["data"].decode("utf-8")   #decodifica el mensaje recibido 
            #elimina igualmente en el caso de una desconexion voluntaria 
            if datos_mensaje.lower() == "cerrar_sesion":
                print(f'--- {usuario["data"].decode("utf-8")} se ha desconectado ---')
                lista_sockets.remove(socket_notificado)
                del clientes[socket_notificado]
                continue
#se imprime el mensaje recibido con los datos de usuario 
            print(f'*Mensaje de {usuario["data"].decode("utf-8")}: {datos_mensaje}*')
            for cliente_socket in clientes:
                if cliente_socket != socket_notificado:
                    cliente_socket.send(usuario['encabezado'] + usuario['data'] + mensaje['encabezado'] + mensaje['data'])
    
    for socket_notificado in exception_sockets:         #itera sobre los sockets con excepciones 
        lista_sockets.remove(socket_notificado)         #elimina el sockect de la lista de sk
        del clientes[socket_notificado]         #elimina la informacion del cliente del diccionario 
        
