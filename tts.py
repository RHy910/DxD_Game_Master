"""Simple TTS wrapper used by the Dungeon Master agent.

This module prefers pyttsx3 (offline, cross-platform). If pyttsx3 is not installed or fails
it falls back to a no-op that prints the text to stdout.

Usage:
    from tts import TTS
    t = TTS()
    t.speak("Hello adventurer")
"""

from typing import Optional


class _NoopTTS:
    def speak(self, text: str):
        # Fallback: print a short prefix so it's visible during tests
        print(f"[TTS fallback] {text[:200].strip()}{'...' if len(text)>200 else ''}")


class TTS:
    def __init__(self, provider: Optional[str] = None, rate: int = 150):
        self._engine = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            try:
                self._engine.setProperty('rate', rate)
            except Exception:
                pass
        except Exception:
            # Not fatal; we'll fallback to printing
            self._engine = None

    def speak(self, text: str):
        if not text:
            return
        if self._engine:
            try:
                # speak async to not block main thread excessively
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                # On any TTS failure, fallback to printing
                print(f"[TTS error] {text[:200].strip()}{'...' if len(text)>200 else ''}")
        else:
            # Fallback
            print(f"[TTS fallback] {text[:200].strip()}{'...' if len(text)>200 else ''}")
