import zmq
import gradio as gr
import base64
from datetime import datetime
from PIL import Image
import io
import json


def create_socket(address, port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{address}:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    return socket


def fetch_reco_camera_stream(address="127.0.0.1"):
    socket = create_socket(address=address, port=5001)
    while True:
        try:
            encoded_image = socket.recv(flags=zmq.NOBLOCK)
            jpg_bytes = base64.b64decode(encoded_image)
            image = Image.open(io.BytesIO(jpg_bytes))
            yield image
        except zmq.error.Again:
            # wait until the next frame is ready

            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            socks = dict(poller.poll(100))
            if socket not in socks:
                continue
            continue

def fetch_reco_part_stream(address="127.0.0.1"):
    socket = create_socket(address=address, port=5002)
    while True:
        try:
            encoded_image = socket.recv(flags=zmq.NOBLOCK)
            jpg_bytes = base64.b64decode(encoded_image)
            image = Image.open(io.BytesIO(jpg_bytes))
            yield image
        except zmq.error.Again:
            # wait until the next frame is ready

            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            socks = dict(poller.poll(100))
            if socket not in socks:
                continue
            continue

def fetch_qr_camera_stream(address="127.0.0.1"):
    socket = create_socket(address=address, port=5003)
    while True:
        try:
            encoded_image = socket.recv(flags=zmq.NOBLOCK)
            jpg_bytes = base64.b64decode(encoded_image)
            image = Image.open(io.BytesIO(jpg_bytes))
            yield image
        except zmq.error.Again:
            # wait until the next frame is ready

            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            socks = dict(poller.poll(100))
            if socket not in socks:
                continue
            continue

# def fetch_log_stream(address="127.0.0.1"):
#     socket = create_socket(address=address, port=5004)
#     formatted_data = ""
#     while True:
#         try:
#             raw_data = socket.recv(flags=zmq.NOBLOCK)
#             data = json.loads(base64.b64decode(raw_data).decode("utf-8"))
#             formatted_data += f"{datetime.fromtimestamp(data['time']).strftime('%Y-%m-%d %H:%M:%S')} - {data['level']} - {data['data']}"
#
#             if formatted_data[-1] != "\n":
#                 formatted_data += "\n"
#             formatted_data = formatted_data[-1000:]
#
#             yield formatted_data
#         except zmq.error.Again:
#             # wait until the next frame is ready
#
#             poller = zmq.Poller()
#             poller.register(socket, zmq.POLLIN)
#             socks = dict(poller.poll(100))
#             if socket not in socks:
#                 continue
#             continue


with gr.Blocks() as ui:
    with gr.Row():
        with gr.Column():
            address_input = gr.Textbox(label="Target address")
            image_output_1 = gr.Image(label="RecoCamera stream", format="jpeg")
            image_output_2 = gr.Image(label="RecoPart stream", format="jpeg")
            image_output_3 = gr.Image(label="QRCamera stream", format="jpeg")
        # with gr.Column():
        #     text_output = gr.Textbox(label="Log stream", lines=10)
    
    address_input.submit(fetch_reco_camera_stream, address_input, image_output_1, api_name="RecoCamera_stream")
    address_input.submit(fetch_reco_part_stream, address_input, image_output_2, api_name="RecoPart_stream")
    address_input.submit(fetch_qr_camera_stream, address_input, image_output_3, api_name="QRCamera_stream")
    # address_input.submit(fetch_log_stream, address_input, text_output, api_name="text_stream")


ui.launch(show_error=True)

