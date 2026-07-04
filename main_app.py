import webview
import threading
import uvicorn
import socket
import time
from backend.main.api_server import app

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

if __name__ == '__main__':
    port = get_free_port()
    
    # Start FastAPI server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Wait for the server to start (simple sleep, in production we might poll the port)
    time.sleep(1)
    
    # Create and start the desktop window
    window = webview.create_window('杯级计算器', f'http://127.0.0.1:{port}/app/', width=414, height=896)
    webview.start(debug=False)
