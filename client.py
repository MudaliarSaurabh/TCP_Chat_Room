import socket
import threading

nickname = input("Enter a nickname: ")
if nickname == 'admin':
    password = input("Enter password for admin:")
stop_thread = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection was refused! Password is wrong.")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused because of ban.')
                    client.close()
                    stop_thread = True
            
            else:
                print(message)
        except Exception as e:
            print(f"An error occurred: {e}")
            client.close()
            break

def write():
    global stop_thread
    while True:
        if stop_thread:
            break
        message = f"{nickname}: {input('')}"
        if message[len(nickname)+2:].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('ascii'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
            else:
                print("Commands can only be executed by the admin!")
        else:
            client.send(message.encode('ascii'))

receiving_thread = threading.Thread(target=receive)
receiving_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
