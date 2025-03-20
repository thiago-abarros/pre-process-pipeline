#!/usr/bin/env python3
import subprocess
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# HTTP server class with CORS support
class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

# Function to run the HTTP server in a separate thread
def run_http_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"Servidor HTTP iniciado na porta {port}")
    httpd.serve_forever()

# Function to terminate processes when the script is interrupted
def terminate_processes(processes, http_server_thread):
    print("\nEncerrando todos os serviços...")

    # Terminate Label Studio
    for process in processes:
        if process.poll() is None:  # If the process is still running
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    # Force termination of the HTTP server thread
    if http_server_thread.is_alive():
        # Unfortunately we can't terminate threads directly in Python
        # The program will be completely terminated, which will end all threads
        print("Encerrando servidor HTTP...")

    print("Todos os serviços foram encerrados.")

def main():
    processes = []

    try:
        # Start the HTTP server on port 8080 in a separate thread
        print("Iniciando o servidor HTTP na porta 8080...")
        http_server_thread = threading.Thread(target=run_http_server, daemon=True)
        http_server_thread.start()

        # Start Label Studio on port 8081
        print("Iniciando o Label Studio na porta 8081...")
        label_studio = subprocess.Popen(["label-studio", "-p", "8081"])
        processes.append(label_studio)

        print("\nServiços iniciados com sucesso!")
        print("  - Servidor HTTP: http://localhost:8080")
        print("  - Label Studio: http://localhost:8081")
        print("\nPressione CTRL+C para encerrar todos os serviços")

        # Keep the script running until the user presses CTRL+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        terminate_processes(processes, http_server_thread)

if __name__ == "__main__":
    main()