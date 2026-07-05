"""
Speech-to-Text: Whisper STT integration.
"""

import tempfile
from pathlib import Path

import whisper


class WhisperTranscriber:
    """Whisper model manager for audio transcription."""
    
    model = None
    
    @classmethod
    def load_model(cls):
        """Load Whisper base model on startup."""
        if cls.model is None:
            cls.model = whisper.load_model("base")
        return cls.model
    
    @classmethod
    def transcribe(cls, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (mp3, wav, m4a, etc.)
            
        Returns:
            Transcribed text
        """
        if cls.model is None:
            cls.load_model()
        
        result = cls.model.transcribe(audio_path)
        return result["text"]
    
    @classmethod
    def audio_to_messages(cls, transcript: str) -> list[dict]:
        """
        Convert audio transcript to message array.
        
        Splits on sentence boundaries to create message chunks.
        All attributed to "unknown" sender (typical for audio input).
        
        Args:
            transcript: Full transcribed text
            
        Returns:
            List of message dicts
        """
        # Split on periods, question marks, exclamation marks
        sentences = transcript.replace("? ", "?|").replace("! ", "!|").split("|")
        
        messages = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                messages.append({
                    "sender": "unknown",
                    "text": sentence,
                    "timestamp": "",  # Backend can fill this
                })
        
        return messages


def get_transcriber() -> WhisperTranscriber:
    """Dependency for FastAPI endpoints."""
    return WhisperTranscriber
