import boto3
import os
import tempfile
import openai

from dotenv import load_dotenv
load_dotenv()

# AWS Polly TTS Setup
polly = boto3.client(
    "polly",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Convert text to speech using AWS Polly
def question_to_speech(text, filename="question.mp3"):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Joanna"
    )
    path = os.path.join(tempfile.gettempdir(), filename)
    with open(path, "wb") as f:
        f.write(response["AudioStream"].read())
    return path

# Transcribe audio using Whisper
# def speech_to_text(audio_path):
#     client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     with open(audio_path, "rb") as f:
#         transcript = client.audio.transcriptions.create(
#             model="whisper-1",
#             file=f
#         )
#     return transcript.text.strip()

import whisper

def speech_to_text(audio_path):
    # Load the Whisper model (choose: tiny, base, small, medium, large)
    model = whisper.load_model("small")
    
    # Transcribe the audio file
    result = model.transcribe(audio_path)
    
    # Return the transcribed text
    return result["text"].strip()

