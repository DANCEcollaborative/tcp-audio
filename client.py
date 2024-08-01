import socket
import json
import datetime
import sounddevice as sd
import numpy as np
import time
import zmq

context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)  # Change the name from 'socket' to 'zmq_socket'

def find_my_ip():
    """Find the IP address of the current machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Use Google's public DNS server to determine own IP
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    finally:
        s.close()
    return IP

def send_IPs_to_PSI():
    """Send the machine's IP addresses for different sensors to the PSI server."""
    req_socket = context.socket(zmq.REQ)
    server_address = "tcp://128.2.204.249:40001"  # Server address
    print("Connecting to server...")
    req_socket.connect(server_address)
    my_ip = find_my_ip()
    time.sleep(1)

    request = json.dumps({
        "sensorVideoText": f"tcp://{my_ip}:40000",
        "sensorAudio": f"tcp://{my_ip}:40001",
        "sensorDOA": f"tcp://{my_ip}:40002",
        "sensorVAD": f"tcp://{my_ip}:40003"
    })

    payload = {
        'message': request,
        'originatingTime': datetime.datetime.utcnow().isoformat()
    }
    print(f"Sending request: {request}")
    req_socket.send_string(json.dumps(payload))

    poller = zmq.Poller()
    poller.register(req_socket, zmq.POLLIN)
    socks = dict(poller.poll(5000))  # 5000ms timeout

    if req_socket in socks and socks[req_socket] == zmq.POLLIN:
        reply = req_socket.recv_string()
        print(f"Received reply: {reply}")
    else:
        print("No reply received within the timeout period.")

    req_socket.close()
    # reply = req_socket.recv_string()
    # print(f"Received reply: {reply}")
    # req_socket.close()

def audio_callback(indata, frames, time, status):
    """This is called for each audio block from the microphone."""
    if status:
        print(status)
    # Ensure indata is in the correct format (int16) for 16-bit PCM.
    vol_normalized_data = (indata * 32767).astype(np.int16)  # Scale float32 data to int16
    sock.sendall(vol_normalized_data.tobytes())

def stream_audio():
    """Stream audio from the microphone."""
    global sock
    host = '128.2.204.249'  # Server IP address
    port = 40001             # Server port

    # Open a TCP socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # Define audio stream parameters
    samplerate = 16000  # Sample rate in Hz
    channels = 1        # Number of audio channels (mono)

    try:
        # Start streaming audio with the specified parameters
        with sd.InputStream(samplerate=samplerate, channels=channels, dtype='float32', callback=audio_callback):
            print("Streaming audio. Press Ctrl+C to stop...")
            while True:
                sd.sleep(1000)  # Keep the main thread alive.
    except Exception as e:
        print(e)
    finally:
        sock.close()

if __name__ == "__main__":
    send_IPs_to_PSI()  # Send IPs first
    time.sleep(3)       # Wait for the server to start
    stream_audio()     # Then start streaming audio
