# import logging
# import os
# from flask import Flask
# from flask_socketio import SocketIO
# from dotenv import load_dotenv
# from deepgram import (
#     DeepgramClient,
#     LiveTranscriptionEvents,
#     LiveOptions,
#     DeepgramClientOptions
# )

# load_dotenv()

# app_socketio = Flask("app_socketio")
# socketio = SocketIO(app_socketio, cors_allowed_origins=['http://127.0.0.1:8000'])

# API_KEY = os.getenv("DEEPGRAM_API_KEY")

# # Set up client configuration
# config = DeepgramClientOptions(
#     verbose=logging.WARN,  # Change to logging.INFO or logging.DEBUG for more verbose output
#     options={"keepalive": "true"}
# )

# deepgram = DeepgramClient(API_KEY, config)

# dg_connection = None

# def initialize_deepgram_connection():
#     global dg_connection
#     # Initialize Deepgram client and connection
#     dg_connection = deepgram.listen.live.v("1")

#     def on_open(self, open, **kwargs):
#         print(f"\n\n{open}\n\n")

#     def on_message(self, result, **kwargs):
#         transcript = result.channel.alternatives[0].transcript
#         if len(transcript) > 0:
#             print(result.channel.alternatives[0].transcript)
#             socketio.emit('transcription_update', {'transcription': transcript})

#     def on_close(self, close, **kwargs):
#         print(f"\n\n{close}\n\n")

#     def on_error(self, error, **kwargs):
#         print(f"\n\n{error}\n\n")

#     dg_connection.on(LiveTranscriptionEvents.Open, on_open)
#     dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
#     dg_connection.on(LiveTranscriptionEvents.Close, on_close)
#     dg_connection.on(LiveTranscriptionEvents.Error, on_error)

#     # Define the options for the live transcription
#     options = LiveOptions(model="nova-2", language="en-US")

#     if dg_connection.start(options) is False: # THIS CAUSES ERROR
#         print("Failed to start connection")
#         exit()

# @socketio.on('audio_stream')
# def handle_audio_stream(data):
#     if dg_connection:
#         dg_connection.send(data)

# @socketio.on('toggle_transcription')
# def handle_toggle_transcription(data):
#     print("toggle_transcription", data)
#     action = data.get("action")
#     if action == "start":
#         print("Starting Deepgram connection")
#         initialize_deepgram_connection()

# @socketio.on('connect')
# def server_connect():
#     print('Client connected')

# @socketio.on('restart_deepgram')
# def restart_deepgram():
#     print('Restarting Deepgram connection')
#     initialize_deepgram_connection()

# if __name__ == '__main__':
#     logging.info("Starting SocketIO server.")
#     socketio.run(app_socketio, debug=True, allow_unsafe_werkzeug=True, port=5001)

import requests
import logging
import os
from flask import Flask, send_file
from flask_socketio import SocketIO
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    DeepgramClientOptions,
    SpeakOptions
)
from utils.qna import bot
from utils.model_class import LanguageModelProcessor

load_dotenv()

app_socketio = Flask("app_socketio")
socketio = SocketIO(app_socketio, cors_allowed_origins=['http://127.0.0.1:8000'])

API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Set up client configuration
config = DeepgramClientOptions(
    verbose=logging.WARN,  # Change to logging.INFO or logging.DEBUG for more verbose output
    options={"keepalive": "true"}
)

deepgram = DeepgramClient(API_KEY, config)
dg_connection = None

# Instantiate the LanguageModelProcessor
lm_processor = LanguageModelProcessor()

def initialize_deepgram_connection():
    global dg_connection
    # Initialize Deepgram client and connection
    dg_connection = deepgram.listen.live.v("1")

    def on_open(self, open, **kwargs):
        print(f"\n\n{open}\n\n")

    def on_message(self, result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        if len(transcript) > 0:
            print(result.channel.alternatives[0].transcript)
            socketio.emit('transcription_update', {'transcription': transcript})
            
            #     # API endpoint
            # api_url = 'http://localhost:1066/chatbs'
            
            # # Prepare the payload
            # payload = {
            #     "question": transcript
            # }
            
            # try:
            #     # Send the POST request to the external API
            #     response = requests.post(api_url, json=payload)
                
            #     # Check if the request was successful
            #     if response.status_code == 200:
            #         api_response = response.json()
            #     else:
            #         api_response = {"answer": "Sorry, there was an issue with the external service."}
            # except Exception as e:
            #         api_response = {"answer": f"Error occurred: {str(e)}"} 
                    
            # print(api_response)               
            
            # Once transcription is received, trigger TTS
            # ans=bot(transcript)
            ans=lm_processor.process(transcript)
            print(ans)
            socketio.emit('tts_update', {'response': ans})
            audio_file_path = synthesize_audio(ans, "aura-asteria-en")  # Nova-2 is the TTS model
            socketio.emit('tts_audio', {'audio_url': f"/static/audio/{os.path.basename(audio_file_path)}"})

    def on_close(self, close, **kwargs):
        print(f"\n\n{close}\n\n")

    def on_error(self, error, **kwargs):
        print(f"\n\n{error}\n\n")

    dg_connection.on(LiveTranscriptionEvents.Open, on_open)
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Close, on_close)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)

    # Define the options for the live transcription
    options = LiveOptions(model="nova-2", language="en-US")

    if dg_connection.start(options) is False:
        print("Failed to start connection")
        exit()

def synthesize_audio(text, model):
    try:
        # Synthesize audio using Deepgram's TTS API
        options = SpeakOptions(model=model)
        audio_folder = os.path.join(app_socketio.static_folder, 'audio')
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
        filename = os.path.join(audio_folder, "output.mp3")
        deepgram.speak.v("1").save(filename, {"text": text}, options)
        return filename
    except Exception as e:
        print(f"Speech synthesis failed: {str(e)}")
        return None

@socketio.on('audio_stream')
def handle_audio_stream(data):
    if dg_connection:
        dg_connection.send(data)

@socketio.on('toggle_transcription')
def handle_toggle_transcription(data):
    print("toggle_transcription", data)
    action = data.get("action")
    if action == "start":
        print("Starting Deepgram connection")
        initialize_deepgram_connection()

@socketio.on('connect')
def server_connect():
    print('Client connected')

@socketio.on('restart_deepgram')
def restart_deepgram():
    print('Restarting Deepgram connection')
    initialize_deepgram_connection()

@app_socketio.route("/static/audio/<filename>")
def serve_audio(filename):
    return send_file(os.path.join(app_socketio.static_folder, "audio", filename), as_attachment=True)

if __name__ == '__main__':
    logging.info("Starting SocketIO server.")
    socketio.run(app_socketio, debug=True, allow_unsafe_werkzeug=True, port=5001)