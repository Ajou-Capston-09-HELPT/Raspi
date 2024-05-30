import socket
import sports
import constant
import threading
import time

rec_state = ""
send_state = ""

HOST = "172.20.10.2"
# Enter IP or Hostname of your server
PORT = 8000

code = ""
msg = ""
server_socket = None
client_socket = None
addr = None
rt = None
st = None

def init():
    global server_socket, client_socket, addr
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("accept before")
    client_socket, addr = server_socket.accept()
    print("accept after")

def receive():
    global code, client_socket, addr, rec_state  
    while True:
        rec_state = client_socket.recv(1024).decode('utf-8')
        time.sleep(1)

 
def send():   
    global msg, client_socket, send_state
    
    while True:
        # if state~~ == ~~: msg = "1"
        timer = 1
        flag = 0
        print("send", send_state)
        if send_state == 'footcheckend' and flag == 0:
            msg = 'a'
            flag = 1
            client_socket.send(msg.encode())
        elif send_state == 'bodycheckend' and flag == 1:
            msg = 'b'
            flag = 2
            client_socket.send(msg.encode())
        elif send_state == 'handcheckend' and flag == 2:
            msg = 'c'
            flag = 3
            client_socket.send(msg.encode())
        elif send_state == 'bandventalldone' and flag == 3:
            msg = 'd'
            flag = 4
            client_socket.send(msg.encode())
        elif send_state == 'notfound':
            msg = 'e'
            client_socket.send(msg.encode())
        elif send_state == 'standby':
            msg = 'f'
            client_socket.send(msg.encode())
        else:
            msg = send_state
            client_socket.send(msg.encode())
        
        time.sleep(timer)


def close():
    global rt, st
    global client_socket, server_socket
    if rec_state == 'socketclose':
        client_socket.close()
    server_socket.close()
    if rt != None:
        rt.join()
    if st != None:
        st.join()


def main():
    global rt, st
    try:
        init()
        rt = threading.Thread(target=receive)
        rt.start()
        st = threading.Thread(target=send)
        st.start()
        
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        close()

if __name__ == "__main__":
	main()