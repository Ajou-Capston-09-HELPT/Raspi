import socket
import sports
import camera
import constant
import threading
import time
import cv2 as cv
rec_state = ""
send_state = ""

HOST = "192.168.79.195"
# Enter IP or Hostname of your server
PORT = 7021

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
        if rec_state == 'onearm' or rec_state == 'bandvent' or rec_state == 'dumbelfront':
            camera.sports = rec_state
        else:
            camera.state = rec_state
        time.sleep(1)

 
def send():   
    global msg, client_socket, send_state
    
    while True:
        timer = 1
        flag = 0
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
        elif send_state == 'alldone' and flag == 3:
            msg = 'd'
            flag = 4
            client_socket.send(msg.encode())
        elif send_state == 'notfound':
            msg = 'e'
            client_socket.send(msg.encode())
        elif send_state == 'standby':
            msg = 'f'
            client_socket.send(msg.encode())
        elif send_state == 'checkend':
            msg = 'g'
            client_socket.send(msg.encode())
        elif send_state == 'Done':
            msg = 'h'
            client_socket.send(msg.encode())
        elif send_state == None:
            continue
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