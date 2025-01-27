import http.server
import socketserver
import webbrowser

host = "localhost"
port = 8000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    pass


if __name__ == "__main__":
    with socketserver.TCPServer((host, port), SimpleHTTPRequestHandler) as httpd:
        url = f"http://{host}:{port}"
        print(f"Server running at {url} (CTRL-C to stop)")
        
        webbrowser.open(url + "/website/accueil/index.html")
        httpd.serve_forever()