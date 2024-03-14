import os

import requests
from pydub import AudioSegment
import logging

from mixins.openai import OpenAIMixin

# Set the export folder from environment variable or use the default value
export_folder = os.environ.get("EXPORT_FOLDER", "./temp")


class Transcriber(OpenAIMixin):  # Mixin included
    def __init__(self, file_instance: str):
        super().__init__()

        # Initialize mixin
        self.initialize_openai()
        self.file_instance = file_instance
        self.transcription_data = {}
        self.transcripts = []
        self.logger = logging.getLogger(__name__)
        self.local_folder = f"{export_folder}/{self.file_instance}"

    def split_audio(self, file_path, chunk_length_ms=480000):  # 8 minutes in milliseconds
        self.logger.info("Splitting audio")
        audio = AudioSegment.from_file(file_path)

        # Calculate the number of chunks
        number_of_chunks = len(audio) // chunk_length_ms + (1 if len(audio) % chunk_length_ms else 0)

        self.logger.info(f"Splitting audio into {number_of_chunks} chunks")

        chunks = []
        for i in range(number_of_chunks):
            # Calculate start and end times
            start_ms = i * chunk_length_ms
            end_ms = start_ms + chunk_length_ms

            # Slice the audio from start_ms to end_ms
            chunk = audio[start_ms:end_ms]

            # Save the chunk to a new file
            chunk_name = f"{self.local_folder}/chunk{i}.mp3"  # Change the extension based on your needs
            chunk.export(chunk_name, format="mp3")
            audio_file = open(chunk_name, "rb")

            self.logger.info(f"Chunk {i + 1} saved to {chunk_name}")

            chunks.append(audio_file)

        return chunks

    def use_or_download_file(self, filepath: str, name: str = None):
        self.create_files_folder()

        # check if the file is local or remote
        if filepath.startswith("http"):
            # download the file
            audio_file = requests.get(filepath)
            file_name = name if name else "audio.mp3"

            self.logger.info(f"Downloading file {file_name}")

            # save the file to a local folder
            with open(f"{self.local_folder}/{file_name}", "wb") as f:
                f.write(audio_file.content)

            audio_file = open(f"{self.local_folder}/{file_name}", "rb")
        else:
            audio_file = open(filepath, "rb")

        return audio_file

    def transcribe(self, audio_path: str, name: str = None):
        audio_file = self.use_or_download_file(audio_path, name)

        self.logger.info("Transcribing audio")
        chunks = self.split_audio(audio_file)

        transcripts = []

        for i, chunk in enumerate(chunks):
            self.logger.info(f"Transcribing chunk {i + 1} of {len(chunks)}, {chunk.name}")

            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=chunk,
            )
            transcripts.append(transcription)

        self.logger.info("Transcription complete")

        full_transcript = ""
        for transcript in transcripts:
            full_transcript += transcript.text

        self.clean_files_folder()

        self.logger.debug(f"Full transcript: {full_transcript}")

        return full_transcript

    def clean_files_folder(self):
        self.logger.debug("Cleaning export folder")
        files = [f for f in os.listdir(self.local_folder)]
        for f in files:
            os.remove(f"{self.local_folder}/{f}")
        self.logger.info(f"Export folder cleaned at {self.local_folder}")

    def create_files_folder(self):
        self.logger.debug("Creating export folder")
        if not os.path.exists(self.local_folder):
            os.makedirs(self.local_folder)
            self.logger.info(f"Export folder created at {self.local_folder}")
