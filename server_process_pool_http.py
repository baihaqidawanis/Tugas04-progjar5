from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan threadpool executor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection,address):
	rcv = b''
	while True:
		try:
			data = connection.recv(4096)
			if data:
				rcv += data
				# Cek apakah sudah ada header lengkap (\r\n\r\n)
				if b'\r\n\r\n' in rcv:
					headers_part, body = rcv.split(b'\r\n\r\n', 1)
					headers_text = headers_part.decode(errors='ignore')
					# Cari Content-Length
					content_length = 0
					for line in headers_text.split('\r\n'):
						if line.lower().startswith('content-length:'):
							content_length = int(line.split(':',1)[1].strip())
					# Jika POST dan ada Content-Length, pastikan body sudah lengkap
					if 'POST' in headers_text.split('\r\n')[0]:
						while len(body) < content_length:
							more = connection.recv(4096)
							if not more:
								break
							body += more
						full_request = headers_part + b'\r\n\r\n' + body
						# Proses request
						hasil = httpserver.proses(full_request.decode('latin1', errors='ignore'))
						connection.sendall(hasil + b"\r\r\n\n")
						connection.close()
						return
					else:
						# GET atau request tanpa body
						hasil = httpserver.proses(rcv.decode('latin1', errors='ignore'))
						connection.sendall(hasil + b"\r\r\n\n")
						connection.close()
						return
			else:
				break
		except OSError as e:
			pass
	connection.close()
	return



def Server():
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	my_socket.bind(('0.0.0.0', 8885))
	my_socket.listen(1)

	with ProcessPoolExecutor(5) as executor:
		while True:
				connection, client_address = my_socket.accept()
				#logging.warning("connection from {}".format(client_address))
				p = executor.submit(ProcessTheClient, connection, client_address)
				the_clients.append(p)
				#menampilkan jumlah process yang sedang aktif
				jumlah = ['x' for i in the_clients if i.running()==True]
				print(jumlah)





def main():
	Server()

if __name__=="__main__":
	main()

