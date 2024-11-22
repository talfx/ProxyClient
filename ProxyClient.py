import requests
import subprocess
import sys
import time
import platform

# Configuration
CENTRAL_SERVER_IP = ''  # Replace with your actual server IP
CENTRAL_SERVER_PORT = 8080
PROXY_PORT = 8899
PROXY_PROTOCOL = 'HTTP'
API_KEY = 'A1B2C3D4E5F6G8'  # Store your API key in an environment variable

def get_local_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            return response.json()['ip']
        else:
            return '127.0.0.1'
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return '127.0.0.1'

def register_proxy(ip, port, protocol):
    url = f'http://{CENTRAL_SERVER_IP}:{CENTRAL_SERVER_PORT}/register'
    data = {
        'apiKey': API_KEY,  # Use environment variable or a config for the API key
        'ip': ip,
        'port': port,
        'protocol': protocol.lower(),
        'osType': platform.system(),  # OS information
        'platform': platform.platform()  # More details
    }
    try:
        response = requests.post(url, json=data, auth=('', ''), timeout=10)
        if response.status_code == 200:
            print('Registeration sent successfully')
            return True
        else:
            print(f'Response: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Error registering proxy: {e}')
    return False

def send_heartbeat(ip, port):
    url = f'http://{CENTRAL_SERVER_IP}:{CENTRAL_SERVER_PORT}/heartbeat'
    data = {'apiKey': API_KEY,'ip': ip, 'port': port}
    try:
        response = requests.post(url, json=data, auth=('', ''), timeout=10)
        if response.status_code == 200:
            print(f'Heartbeat sent successfully from {ip}:{port}')
        else:
            print(f'Failed to send heartbeat. Status code: {response.status_code}')
            print(f'Response: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'Error sending heartbeat from {ip}:{port}: {e}')

def start_heartbeat(ip, port):
    while True:
        try:
            time.sleep(300)  # 5 minutes
            send_heartbeat(ip, port)
        except Exception as e:
            print(f'Error in heartbeat process: {e}')
            time.sleep(10)  # Wait before restarting heartbeat

def start_proxy_server(port, protocol):
    # Determine the protocol flags
    protocol_flags = []
    if protocol.upper() == 'HTTPS':
        protocol_flags.extend(['--enable-https'])
    elif protocol.upper() == 'SOCKS5':
        protocol_flags.extend(['--enable-socks5'])

    # Construct the command
    command = [
        sys.executable,  # Use the current Python interpreter
        '-m', 'proxy',   # Use proxy.py as a module
        '--hostname', '0.0.0.0',
        '--port', str(port),
        '--num-workers', '1'
    ] + protocol_flags

    print(f"Starting proxy server with command: {' '.join(command)}")
    
    # Start the proxy server using subprocess, without blocking
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Proxy server running on port {port} with protocol {protocol}.")
        return True
    except Exception as e:
        print(f"Error starting proxy server: {e}")
        return False

if __name__ == '__main__':
    ip = get_local_ip()
    port = PROXY_PORT
    protocol = PROXY_PROTOCOL
    while True:
        try:
            if start_proxy_server(port, protocol):
                if register_proxy(ip, port, protocol):
                     start_heartbeat(ip, port)
        except Exception as e:
            print(f"{e} /n Restarting in 20 min.......")
            time.sleep(1200)
            continue
#python ProxyClient.py
