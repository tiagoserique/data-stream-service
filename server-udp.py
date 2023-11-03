import sys
import time
import socket
import pickle

BUFFER_SIZE = 1024
CONECT_MSG  = "request_connection"


def check_arguments():
    """
    Checa se os argumentos foram passados corretamente e retorna os valores
    passados. Caso contrario, imprime uma mensagem de erro e encerra o programa.

    Retorna:
        porta (int): porta do socket
        delay (int): intervalo de tempo entre cada mensagem
    """

    if len(sys.argv) != 3:
        print("Erro - Uso: python3 server-udp.py <porta> <intervalo de tempo>")
        sys.exit(1)

    port = int(sys.argv[1])
    delay = int(sys.argv[2])

    return port, delay


def start_server(port, delay):
    """
    Inicia o socket do server e retorna o socket, o endereco do socket e o 
    intervalo de tempo entre cada mensagem.
    """

    print("Iniciando server...")

    #configura o socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)

    # pega nome do server
    host_name = socket.gethostname()
    
    # pega o endereco IP a partir do nome do server
    host_ip = socket.gethostbyname(host_name)
    if (host_ip == 0):
        print("Erro - Host desconhecido:", host_name)
        sys.exit(1)

    # monta endereco do socket
    sock_addr = (host_ip, port)

    # configura timeout
    timeout = min(delay, 0.2)
    sock.settimeout(timeout)
    delay = delay - timeout

    # da bind no socket com o endereco
    sock.bind(sock_addr)

    print(f"Server {host_name} iniciado")
    print(f"IP: {host_ip}")
    print(f"Porta: {port}")

    return sock, delay


def wait_for_clients(clients_list):
    """
    Espera a conexao de um client.
    """

    print("Esperando conexao...")

    while (True):
        # espera mensagem de conexao
        try:
            msg, client_addr = sock.recvfrom(BUFFER_SIZE)
            
            # verifica se a mensagem recebida e de conexao
            if msg.decode() == CONECT_MSG:
                print(f"Conexao estabelecida - cliente: {client_addr}")
                clients_list.append(client_addr)
            else:
                print("Erro - Mensagem de conexao invalida")

        except socket.timeout:
            # minimo de 3 clientes
            if (len(clients_list) >= 3):
                break

        except Exception as e:
            print("Erro - Falha ao receber mensagem de conexao:", e)
            sys.exit(1)


def stream(sock, clients_list, message):
    """
    Envia a mensagem para todos os clientes da lista.
    """

    for client in clients_list:
        try:
            sock.sendto(message, client)
        except Exception as e:
            print(f"Erro - Falha ao enviar mensagem de conexao: {e}")
            

def main(sock, delay):
    clients_list = list()

    #espera conexao
    wait_for_clients(clients_list)

    #manda o numero de mensagens
    message_bytes = pickle.dumps(10)
    stream(sock, clients_list, message_bytes)

    for i in range(0, 10):
        message_bytes = pickle.dumps(i)
        
        stream(sock, clients_list, message_bytes)

        time.sleep(delay)

    print("Mensagens enviadas aos clientes! Terminando programa...")

if __name__ == "__main__":
    port, delay = check_arguments()
    sock, delay = start_server(port, delay)
    main(sock, delay)
