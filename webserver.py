import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import hashlib

# put an existing folder here
avatar_folder = "pics"

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            print self.path
            if self.path == "/":
                f = open(curdir + sep + "index.html")

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            if not ".." in self.path:
                url_elements = self.path.split(".");
                if not len(url_elements) == 2:
                    self.wfile.write("<HTML>Only files of type PNG provided. Add \".png\" to the URL.<BR><BR>");
                    return
                    
                [filename, type] = url_elements
                if not "png" in type:
                    self.wfile.write("<HTML>Only files of type PNG provided. Add \".png\" to the URL.<BR><BR>");
                    return
                    
                f = open(curdir + sep + avatar_folder + sep + filename)

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
        global rootnode
        global avatar_folder
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
        avatar_url = "/" + address_hash + ".png"
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

