import string,cgi,time
from os import curdir, sep, path
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import hashlib

# put an existing folder here
avatar_folder = "pics"
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
                
                if path.isfile(filepath):
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
        f = open(curdir + sep + avatar_folder + sep + address_hash, "w")
        f.write(upfile)
        f.close()
        print "Avatar uploaded for", address, address_hash
        avatar_url = "/avatar/" + address_hash
        self.wfile.write("<HTML>Avatar updated and can be retrieved <a href=\"" + avatar_url + "\">here.</a><BR><BR>");

def main():
    try:
        server = HTTPServer(('', 80), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

