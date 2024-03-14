import os

import requests
from pydub import AudioSegment

from mixins.openai import OpenAIMixin

# Set the export folder from environment variable or use the default value
export_folder = os.environ.get("EXPORT_FOLDER", "./temp")


class Transcriber(OpenAIMixin):  # Mixin included
    def __init__(self):
        # Initialize mixin
        self.initialize_openai()
        self.transcription_data = {}
        self.transcripts = []

    def split_audio(self, file_path, chunk_length_ms=480000):  # 8 minutes in milliseconds
        print("Splitting audio")
        audio = AudioSegment.from_file(file_path)

        # Calculate the number of chunks
        number_of_chunks = len(audio) // chunk_length_ms + (1 if len(audio) % chunk_length_ms else 0)

        print(f"Splitting audio into {number_of_chunks} chunks")

        chunks = []
        for i in range(number_of_chunks):
            # Calculate start and end times
            start_ms = i * chunk_length_ms
            end_ms = start_ms + chunk_length_ms

            # Slice the audio from start_ms to end_ms
            chunk = audio[start_ms:end_ms]

            # Save the chunk to a new file
            chunk_name = f"{export_folder}/chunk{i}.mp3"  # Change the extension based on your needs
            chunk.export(chunk_name, format="mp3")
            audio_file = open(chunk_name, "rb")

            print(f"Chunk {i + 1} saved to {chunk_name}")

            chunks.append(audio_file)

        return chunks

    def useOrDownloadModel(self, filepath):
        self.create_export_folder()

        # check if the file if local or remote
        if filepath.startswith("http"):
            # download the file
            audio_file = requests.get(filepath)

            # save the file to a local folder
            with open(f"{export_folder}/audio.mp3", "wb") as f:
                f.write(audio_file.content)

            audio_file = open(f"{export_folder}/audio.mp3", "rb")
        else:
            audio_file = open(filepath, "rb")

        return audio_file

    def transcribe(self, audio_path: str):
        audio_file = self.useOrDownloadModel(audio_path)

        print("Transcribing audio")
        chunks = self.split_audio(audio_file)

        transcripts = []

        for i, chunk in enumerate(chunks):
            print(f"Transcribing chunk {i + 1} of {len(chunks)}, {chunk.name}")

            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=chunk,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            transcripts.append(transcription)

        print("Transcription complete")
        print(transcripts)

        full_transcript = ""
        for transcript in transcripts:
            full_transcript += transcript.text

        self.clean_export_folder()

        return full_transcript


    def clean_export_folder(self):
        print("Cleaning export folder")
        files = [f for f in os.listdir(export_folder)]
        for f in files:
            os.remove(f"{export_folder}/{f}")

    def create_export_folder(self):
        print("Creating export folder")
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        else:
            self.clean_export_folder()