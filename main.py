import openai

def transcribe_file(audio_file, model="whisper-1"):
  """Transcribes an audio file using OpenAI's Whisper model."""
  with open(audio_file, "rb") as f:
    transcript = openai.Audio.transcribe(model, f)
  return transcript["text"]

def main():
  """Transcribes an audio file and prints the results."""
  audio_file = "audio.mp3"
  transcript = transcribe_file(audio_file)
  print(transcript)

if __name__ == "__main__":
  main()