import sys
import pickle
import socket
import pandas as pd
import datetime


BUFFER_SIZE = 1024
CONECT_MSG  = "request_connection"
client_file = "log-execucao-client-" + str(datetime.datetime.now()) + ".txt"


def logging(message, mode="a"):
    """
    Escreve a mensagem no arquivo de log.

    Retorna:
        message (str): mensagem a ser escrita no arquivo de log
        mode (str): modo de escrita no arquivo de log
    """
    try:
        with open(client_file, mode) as arquivo:
            arquivo.write(message+"\n")
    except FileNotFoundError:
        with open(client_file, "w+") as arquivo:
            arquivo.write(message)


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

    Retorna:
        sock (socket): socket do client
        sock_addr (tuple): endereco do socket
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
    logging("Socket configurado", "w")

    return sock, sock_addr


def start_conection(sock, sock_addr):
    """
    Inicia a conexao com o server e retorna o numero de pacotes a serem recebidos.
    
    Retorna:
        n_pckts (int): numero de pacotes a serem recebidos
    """

    print("Conectando ao server...")
    logging("Conectando ao server...")

    n_pckts = 0
    while (n_pckts == 0):
        try:
            sock.sendto(CONECT_MSG.encode(), sock_addr)

            sock.settimeout(0.1)
            message_bytes, _ = sock.recvfrom(BUFFER_SIZE)
            n_pckts = pickle.loads(message_bytes)
        except socket.timeout:
            pass
        except Exception as e:
            print("Erro - Falha ao enviar mensagem de conexao:", e)
            sys.exit(1)

    print("Conexao iniciada")
    logging("Conexao iniciada")

    return n_pckts


def main(sock, sock_addr):
    n_pckts = start_conection(sock, sock_addr)

    # inicia variaveis de recebimento de mensagens
    previous_number = -1
    arrived = [0] * n_pckts
    disordered = list()

    # coloca timeout de 1 segundo
    sock.settimeout(1)

    dfs = pd.DataFrame()

    # recebe as mensagens
    while (True):
        try:
            message_bytes, _ = sock.recvfrom(BUFFER_SIZE)
            
            message = pickle.loads(message_bytes) 
            received_number = message.index.values.astype(int)[0]
            dfs = pd.concat([dfs,message])

            if (received_number < previous_number):
                disordered.append(received_number)
            
            # registra que a mensagem chegou
            arrived[received_number-1] = 1

            previous_number = received_number

            print(f"recebi a mensagem:  {received_number} || {message}")
            logging(f"recebi a mensagem: {received_number} || {message}")
        
        except socket.timeout:
            break

    print(str(dfs.count()))
    print("Mensagens recebidas! Cliente encerrado!")
    print("Quantidade de mensagens recebidas:", sum(arrived))
    print("Quantidade de mensagens perdidas:", n_pckts - sum(arrived))
    print("Quantidade de mensagens fora de ordem:", len(disordered))

    logging(str(dfs.count()))
    logging("Mensagens recebidas! Cliente encerrado!")
    logging(f"Quantidade de mensagens recebidas: {sum(arrived)}")
    logging(f"Quantidade de mensagens perdidas: {n_pckts - sum(arrived)}")
    logging(f"Quantidade de mensagens fora de ordem: {len(disordered)}")



if __name__ == "__main__":
    server_host_name, server_port = check_arguments()
    sock, sock_addr = socket_configuration(server_host_name, server_port)
    main(sock, sock_addr)
