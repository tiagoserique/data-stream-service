import sys
import pickle
import socket

BUFFER_SIZE = 1024
CONECT_MSG  = "request_connection"


def check_arguments():
    """
    Checa se os argumentos foram passados corretamente e retorna os valores
    passados. Caso contrario, imprime uma mensagem de erro e encerra o programa.

    Retorna:
        server_host_name (str): nome do server a ser conectado
        server_port (int): porta do server
    """

    if len(sys.argv) != 3:
        print("Erro - Uso: python3 client-udp.py <host> <port>")
        sys.exit(1)

    server_host_name = sys.argv[1]
    server_port = int(sys.argv[2])

    return server_host_name, server_port


def socket_configuration(server_host_name, server_port):
    """
    Configura o socket do client e retorna o socket e o endereco do socket.
    """

    # pega o endereco IP do server a partir do nome
    server_host_ip = socket.gethostbyname(server_host_name)
    if (server_host_ip == 0):
        print("Erro - Host desconhecido:", server_host_name)
        sys.exit(1)

    # abre o socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)

    # monta endereco do socket
    sock_addr = (server_host_ip, server_port)

    print("Socket configurado")

    return sock, sock_addr


def start_conection(sock, sock_addr):
    print("Conectando ao server...")

    try:
        sock.sendto(CONECT_MSG.encode(), sock_addr)
    except Exception as e:
        print("Erro - Falha ao enviar mensagem de conexao:", e)
        sys.exit(1)

    print("Conexao iniciada")


def main(sock, sock_addr):
    start_conection(sock, sock_addr)

    sock.settimeout(None)
    
    message_bytes, _ = sock.recvfrom(BUFFER_SIZE)
    n_msg = pickle.loads(message_bytes) 

    # inicia variaveis de recebimento de mensagens
    previous_number = -1
    arrived = [0] * n_msg
    disordered = list()

    # coloca timeout de 1 segundo
    sock.settimeout(1)

    # recebe as mensagens
    while (True):
        try:
            message_bytes, _ = sock.recvfrom(BUFFER_SIZE)
            received_number = pickle.loads(message_bytes) 

            if (received_number < previous_number):
                disordered.append(received_number)
            
            # registra que a mensagem chegou
            arrived[received_number] = 1

            previous_number = received_number

            print("recebi a mensagem: ", received_number)
        
        except socket.timeout:
            break

    print("Mensagens recebidas! Cliente encerrado!")


if __name__ == "__main__":
    server_host_name, server_port = check_arguments()
    sock, sock_addr = socket_configuration(server_host_name, server_port)
    main(sock, sock_addr)
