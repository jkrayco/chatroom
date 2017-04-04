import socket
import sys
import select
import thread

serv_addr = '127.0.0.1'
port = 12314
keep_alive = 1

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((serv_addr, port))

print("Connected to chat server.")
print("IP Address:", serv_addr)
print("Port:", port)

def send():
	while 1:
		msg_out=sys.stdin.readline()
		msg_out=msg_out.encode('utf-8')
		c.send(msg_out)
		

thread.start_new_thread(send, ())

while 1:
	try:
		msg_in = c.recv(1024)
		msg_in = msg_in.decode('utf-8')
		print(msg_in)
		if msg_in == '':
			c.close()
			break
	except:
		c.close()
		break
