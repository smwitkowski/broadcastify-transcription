import logging
import flask
import openai
import os
from google.cloud import secretmanager
from pydub import AudioSegment
from pyannote.audio import Pipeline

# Set up logging
logging.basicConfig(level=logging.INFO)

logging.info('Application starting...')

def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    logging.info(f'Accessing secret version for project: {project_id}, secret: {secret_id}, version: {version_id}')

    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

OPENAI_API_KEY = access_secret_version(1076126751560, "openai-api-key", "latest")
HF_KEY = access_secret_version(1076126751560, "huggingface-api-key", "latest")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

logging.info('Loading pipeline...')
PIPELINE = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=HF_KEY)

app = flask.Flask(__name__)

@app.route("/transcribe", methods=['POST'])
def transcribe():
    logging.info('Received a POST request for transcription')

    audio_file = flask.request.files["audio_file"]
    
    # Check if the post request has the file part
    if 'audio_file' not in flask.request.files:
        logging.error('No file part in the request')
        flask.abort(400, description="No file part")

    # If the user does not select file, the browser might submit an empty file part without filename
    if audio_file.filename == '':
        logging.error('No file selected in the request')
        flask.abort(400, description="No selected file")

    # Get the file type extension (e.g. mp3, wav, etc.)
    extension = os.path.splitext(audio_file.filename)[1]

    # Save the file to /data/input directory
    audio_filepath = os.path.join('/data/input', audio_file.filename)
    audio_file.save(audio_filepath)

    logging.info(f'Saved audio file to: {audio_filepath}')

    # Open the file for reading
    audio_content = AudioSegment.from_file(audio_filepath, format=extension[1:])
    # Take a random 30 second sample of the audio file
    audio_content = audio_content[:60000*5]
    stripped_audio = audio_content.strip_silence(silence_len=1000, silence_thresh=-50, padding=1000)
    stripped_audio.export('audio_stripped.wav', format='wav')
    # Transcribe the audio file
    logging.info('Transcribing the audio file...')
    diariztion = PIPELINE('audio_stripped.wav', min_speakers=2, max_speakers=20)

    transcript = ""

    for timestamp, _, speaker in diariztion.itertracks(yield_label=True):
        logging.info(f"Transcribing speaker {speaker} at timestamp {timestamp}")
        audio = stripped_audio[timestamp.start * 1000:timestamp.end * 1000]
        # Save pyannote.core.annotation.Annotation to wav file using pyannote.core.audio.Audio
        audio.export('temp.wav', format='wav')
        with open('temp.wav', 'rb') as audio_file:
            audio_transcript = openai.Audio.transcribe("whisper-1", audio_file)
            if 'text' in audio_transcript.keys():
                transcript += f"{speaker}: {audio_transcript['text']}\n"
                logging.info(f"Transcript: {transcript}")
            else:
                continue
        os.remove('temp.wav')
        
    logging.info('Finished transcribing the audio file')
    return transcript

if __name__ == "__main__":
    logging.info('Starting Flask server...')
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
