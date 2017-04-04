import socket
import select
import sys
import datetime

serv_ip = '127.0.0.1'
port = 12314
bufflen = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)
s.bind((serv_ip, port))
s.listen(10)
keep_alive=1
inputs = [s]
outputs=[]
names = {}
addresses = {}


while keep_alive:
	r_ready, w_ready, err = select.select(inputs, outputs, [], 0)
	for sample in r_ready:
		if sample == s:
			c, c_addr = s.accept()
			name=c_addr[0]	#Address
			inputs.append(c)	#Message + Socket
			sys_msg="Welcome to the chat room!"
			sys_msg=sys_msg.encode('utf-8')
			c.send(sys_msg)
			c.send("type /help to see commands".encode('utf-8'))
			sys_msg=name+" has entered the room."
			sys_msg=sys_msg.encode('utf-8')
			for o in outputs:
				o.send(sys_msg)
			outputs.append(c)
			names[c] = name
			addresses[c]=c_addr[0]

		else:
			buff = sample.recv(1024)
			buff=buff.decode('utf-8')
			if buff:
				if buff[0] == '/': #COMMANDS!
					buff=buff[1:]
					bufftry=buff[0:11]
					bufftry2=buff[0:9]
					bufftry3=buff[0:8]
					if buff == 'quit\n':
						sample.close()
						msg = names[sample].strip('\n')+" has left."
						outputs.remove(sample)
						inputs.remove(sample)
						del names[sample]
						del addresses[sample]
					
					elif bufftry == 'changename ':
						buff=buff[11:]
						if buff[0] == '\n':
							sample.send("Blank username is not allowed!".encode('utf-8'))
							continue
						elif buff in names.values():
							if names[sample] == buff:
								sample.send("But... that's already your name... I'm confused...".encode('utf-8'))
							else:
								sample.send("That username is already taken!".encode('utf-8'))
							continue
						else:
							msg = names[sample].strip('\n')+" is now "+buff
							names[sample]=buff

					elif buff == 'time\n':
						buff=datetime.datetime.time(datetime.datetime.now())
						sample.send(str(buff).encode('utf-8'))
						continue

					elif bufftry3 == 'pm ':
						buff = buff[8:]
						if buff[0] == '\n':
							sample.send("Nobody to talk to, nothing to say... sad...".encode('utf-8'))
							continue
						buff = list(buff.partition(' '))
						if buff[1] != ' ':
								sample.send("Why pm if you won't talk?".encode('utf-8'))
								continue
						buff[0]=buff[0]+'\n'
						if buff[0] in names.values():
							if names[sample] == buff[0]:
								sample.send("But... this is you... Talking to yourself?".encode('utf-8'))
							else:
								bufftry3 = list(names.keys())[list(names.values()).index(buff[0])]
								bufftry3.send((names[sample].strip()+'(pm):'+buff[2]).encode('utf-8'))
							continue
						else:
							sample.send("There is no such user.".encode('utf-8'))
							continue

					elif buff == 'help\n':
						sample.send('Any text not preceeded by a \'/\' is treated as a broadcast message.\n'.encode('utf-8'))
						sample.send('/changename [newname] - sets current username to newname.\n'.encode('utf-8'))
						sample.send('You may not choose a username currently in use. (Please don\'t try)\n'.encode('utf-8'))
						sample.send('/pm [username] [message] - private message to username (Recommended for secrets)\n'.encode('utf-8'))
						sample.send('/delaypm [n] [username] [message] - delays private message to username by n seconds\n'.encode('utf-8'))
						sample.send('/delay [n] - delays message by n seconds\n'.encode('utf-8'))
						sample.send('Press Ctrl+C - disconnects from socket and exits\n'.encode('utf-8'))
						continue

					else:
						sample.send("Invalid Command.".encode('utf-8'))
						continue


				else:
					msg = names[sample].strip('\n')+":"+buff
				print(msg)
				msg = msg.encode('utf-8')
				for o in outputs:
					if o != sample:
						o.send(msg)
			else:
				msg = names[c_addr]+" has been disconnected."
				sample.close()
				outputs.remove(sample)
				inputs.remove(sample)
				del names[sample]
				del addresses[sample]
				for o in outputs:
					o.send(msg)
s.close()
