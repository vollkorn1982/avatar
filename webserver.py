import string, cgi, time
from os import curdir, sep, path, remove
from glob import glob
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import hashlib
import Image
import urlparse
import ssl

# configure these values
avatar_folder = "pics"
http_port = 8080
use_https = True
https_cert = '/opt/avatar/hongkong.everbase.net-cert.pem'
https_key = '/opt/avatar/hongkong.everbase.net-key.pem'
https_ca = '/opt/avatar/everbase.net-cert.pem'
johndoe_filename = "johndoe"
johndoe_count = 9

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path == "/":
                f = open(curdir + sep + "index.html")

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if self.path.startswith("/avatar"):
                filename = self.path.split("?")[0]
                filename = filename.split("/")[-1]
            
                if not len(filename) == 32:
                    self.wfile.write("<HTML>Invalid avatar hash string. Hash string needs to be exactly 32 characters long.<BR><BR>");
                    return
                
                if not all(c in string.hexdigits for c in filename):
                    self.wfile.write("<HTML>Invalid avatar hash string. Only hexadecimal characters accepted.<BR><BR>");
                    return

                filepath = curdir + sep + avatar_folder + sep + filename
                
                parsed = urlparse.urlparse(self.path)

                size = -1
                if parsed.query:
                    param_s = urlparse.parse_qs(parsed.query)
                    print "s=", param_s
                    if 's' in param_s:
                        size = int(param_s['s'][0])
                
                if path.isfile(filepath):
                
                    if size >= 0:
                        filepathsize = filepath + "_" + str(size)
                        
                        if not path.isfile(filepathsize):
                            im = Image.open(filepath)
                            im.thumbnail([size, size], Image.ANTIALIAS)
                            im.save(filepathsize, "PNG")
                            
                        f = open(filepathsize)
                            
                    else:
                        f = open(filepath)
                else:
                    f = open(curdir + sep + johndoe_filename + str(int(filename, 16) % johndoe_count))

                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
                                
            self.send_error(404,'File Not Found: %s' % self.path)

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            query=cgi.parse_multipart(self.rfile, pdict)
        self.send_response(301)
        self.end_headers()

        address = query.get('address')[0]
        if not address:
            self.wfile.write("<HTML>No email address provided.<BR><BR>");
            return

        upfile = query.get('upfile')[0]
        if not upfile:
            self.wfile.write("<HTML>No file provided.<BR><BR>");
            return           

        address_hash = hashlib.md5(address).hexdigest()
        
        filename = curdir + sep + avatar_folder + sep + address_hash
        
        for f in glob (filename + "*"):
            remove(f)
        
        f = open(curdir + sep + avatar_folder + sep + address_hash, "w")
        f.write(upfile)
        f.close()
        print "Avatar uploaded for", address, address_hash
        avatar_url = "/avatar/" + address_hash
        self.wfile.write("<HTML>Avatar updated and can be retrieved <a href=\"" + avatar_url + "\">here.</a><BR><BR>");

class ForkingHTTPServer(HTTPServer, SocketServer.ForkingMixIn):
    def finish_request(self, request, client_address):
        request.settimeout(30.0)
        # "super" can not be used because BaseServer is not created from object
        HTTPServer.finish_request(self, request, client_address)

def main():
    try:
        server = ForkingHTTPServer(('', http_port), MyHandler)
        if use_https:
            try:
                server.socket = ssl.wrap_socket(server.socket, keyfile=https_key, certfile=https_cert, ca_certs=https_ca, server_side=True)
            except ssl.SSLError, err:
                if err.args[1].find("sslv3 alert") == -1:
                    raise
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

