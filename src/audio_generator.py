from gtts import gTTS

def create_audio(text, filename="output.mp3"):
    """Genera un archivo de audio a partir de un texto usando gTTS."""
    tts = gTTS(text=text, lang='es', tld='es')
    tts.save(filename)
