import socket
import sys
import os

def send_request(request, host='localhost', port=8885):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(request.encode())
    response = b''
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data
    s.close()
    return response

def list_files():
    req = "GET /list HTTP/1.0\r\n\r\n"
    resp = send_request(req)
    print("[LIST FILES]\n", resp.decode(errors='ignore'))

def upload_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        filedata = f.read()
    headers = f"POST /upload HTTP/1.0\r\nX-Filename: {filename}\r\nContent-Length: {len(filedata)}\r\n\r\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 8885))
    s.sendall(headers.encode() + filedata)
    response = b''
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data
    s.close()
    print(f"[UPLOAD {filename}]\n", response.decode(errors='ignore'))

def delete_file(filename):
    req = f"GET /delete?file={filename} HTTP/1.0\r\n\r\n"
    resp = send_request(req)
    print(f"[DELETE {filename}]\n", resp.decode(errors='ignore'))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client_implementation.py [list|upload|delete] [filename]")
        sys.exit(1)
    op = sys.argv[1]
    if op == 'list':
        list_files()
    elif op == 'upload' and len(sys.argv) == 3:
        upload_file(sys.argv[2])
    elif op == 'delete' and len(sys.argv) == 3:
        delete_file(sys.argv[2])
    else:
        print("Usage: python client_implementation.py [list|upload|delete] [filename]")
