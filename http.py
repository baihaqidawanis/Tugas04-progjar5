import os
import sys
import uuid
from glob import glob
from datetime import datetime
import urllib.parse
import threading

class HttpServer:
	def __init__(self):
		self.sessions={}
		self.types={}
		self.types['.pdf']='application/pdf'
		self.types['.jpg']='image/jpeg'
		self.types['.txt']='text/plain'
		self.types['.html']='text/html'
	def log(self, msg):
		print(f"[PID {os.getpid()}][TID {threading.get_ident()}] {msg}")
	def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
		tanggal = datetime.now().strftime('%c')
		resp=[]
		resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
		resp.append("Date: {}\r\n" . format(tanggal))
		resp.append("Connection: close\r\n")
		resp.append("Server: myserver/1.0\r\n")
		resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
		for kk in headers:
			resp.append("{}:{}\r\n" . format(kk,headers[kk]))
		resp.append("\r\n")

		response_headers=''
		for i in resp:
			response_headers="{}{}" . format(response_headers,i)
		#menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
		#response harus berupa bytes
		#message body harus diubah dulu menjadi bytes
		if isinstance(messagebody, str):
			messagebody = messagebody.encode()

		response = response_headers.encode() + messagebody
		#response adalah bytes
		return response

	def proses(self,data):
		self.log(f"Request received: {repr(data[:100])} ...")
		# Pisahkan header dan body
		if '\r\n\r\n' in data:
			headers_part, body = data.split('\r\n\r\n', 1)
		else:
			headers_part = data
			body = ''
		requests = headers_part.split("\r\n")
		baris = requests[0]
		all_headers = [n for n in requests[1:] if n!='']

		j = baris.split(" ")
		try:
			method = j[0].upper().strip()
			if (method=='GET'):
				object_address = j[1].strip()
				self.log(f"Processing GET {object_address}")
				return self.http_get(object_address, all_headers)
			if (method=='POST'):
				object_address = j[1].strip()
				self.log(f"Processing POST {object_address}")
				return self.http_post(object_address, all_headers, body)
			else:
				self.log(f"Bad request method: {method}")
				return self.response(400,'Bad Request',b'',{})
		except IndexError:
			self.log("IndexError in parsing request")
			return self.response(400,'Bad Request',b'',{})
	def http_get(self,object_address,headers):
		self.log(f"http_get called: {object_address}")
		files = glob('./*')
		#print(files)
		thedir='./'
		if (object_address == '/'):
			return self.response(200,'OK',b'Ini Adalah web Server percobaan',dict())

		# Fitur 1: Melihat daftar file pada satu direktori
		if (object_address == '/list'):
			file_list = os.listdir(thedir)
			file_list_str = '\n'.join(file_list)
			headers = {'Content-type': 'text/plain'}
			return self.response(200, 'OK', file_list_str.encode(), headers)

		if (object_address == '/video'):
			return self.response(302,'Found',b'',dict(location='https://youtu.be/katoxpnTf04'))
		if (object_address == '/santai'):
			return self.response(200,'OK',b'santai saja',dict())

		# Fitur 3: Menghapus file
		if object_address.startswith('/delete'):
			self.log(f"Delete request: {object_address}")
			parsed = urllib.parse.urlparse(object_address)
			params = urllib.parse.parse_qs(parsed.query)
			filename = params.get('file', [None])[0]
			if filename:
				filepath = os.path.join(thedir, filename)
				if os.path.exists(filepath):
					try:
						os.remove(filepath)
						self.log(f"File {filename} deleted")
						return self.response(200, 'OK', f'File {filename} deleted'.encode(), {'Content-type': 'text/plain'})
					except Exception as e:
						return self.response(500, 'Internal Server Error', str(e).encode(), {'Content-type': 'text/plain'})
				else:
					return self.response(404, 'Not Found', b'File not found', {'Content-type': 'text/plain'})
			else:
				return self.response(400, 'Bad Request', b'No file specified', {'Content-type': 'text/plain'})

		object_address=object_address[1:]
		if thedir+object_address not in files:
			return self.response(404,'Not Found',b'',{})
		fp = open(thedir+object_address,'rb') #rb => artinya adalah read dalam bentuk binary
		#harus membaca dalam bentuk byte dan BINARY
		isi = fp.read()
		
		fext = os.path.splitext(thedir+object_address)[1]
		content_type = self.types.get(fext, 'application/octet-stream')
		
		headers={}
		headers['Content-type']=content_type
		
		return self.response(200,'OK',isi,headers)

	def http_post(self,object_address,headers,body=None):
		self.log(f"http_post called: {object_address}")
		# Fitur 2: Mengupload sebuah file
		if object_address.startswith('/upload'):
			filename = None
			for h in headers:
				if h.lower().startswith('x-filename:'):
					filename = h.split(':',1)[1].strip()
			if not filename:
				self.log('No filename specified in X-Filename header')
				return self.response(400, 'Bad Request', b'No filename specified in X-Filename header', {'Content-type': 'text/plain'})
			try:
				if body is None:
					self.log(f'No file content provided for {filename}')
					return self.response(400, 'Bad Request', b'No file content provided', {'Content-type': 'text/plain'})
				if isinstance(body, str):
					body = body.encode('latin1')
				self.log(f'Writing file {filename} with size {len(body)} bytes')
				with open(filename, 'wb') as f:
					f.write(body)
				self.log(f'File {filename} written successfully')
				headers_resp = {'Content-type': 'text/plain'}
				return self.response(200, 'OK', f'File {filename} uploaded'.encode(), headers_resp)
			except Exception as e:
				self.log(f'Error writing file {filename}: {e}')
				return self.response(500, 'Internal Server Error', str(e).encode(), {'Content-type': 'text/plain'})
		headers ={}
		isi = b"kosong"
		return self.response(200,'OK',isi,headers)
		
			 	
#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
	httpserver = HttpServer()
	d = httpserver.proses('GET testing.txt HTTP/1.0')
	print(d)
	d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
	print(d)
	#d = httpserver.http_get('testing2.txt',{})
	#print(d)
#	d = httpserver.http_get('testing.txt')
#	print(d)















