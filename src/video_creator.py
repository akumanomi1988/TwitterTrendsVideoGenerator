from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import requests
import configparser

# Leer el archivo de configuración
config = configparser.ConfigParser()
config.read('config.ini')

PEXELS_API_KEY = config['PEXELS']['API_KEY']

def download_background_video(query, filename="background.mp4"):
    """Descarga un video de fondo desde Pexels."""
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    headers = {"Authorization": f"Bearer {PEXELS_API_KEY}"}

    response = requests.get(url, headers=headers)
    video_url = response.json()['videos'][0]['video_files'][0]['link']

    video_response = requests.get(video_url)

    with open(filename, 'wb') as f:
        f.write(video_response.content)

def create_video(text, audio_file, background_file="background.mp4"):
    """Crea un video a partir de un texto, un archivo de audio y un video de fondo usando moviepy."""
    background_clip = VideoFileClip(background_file).subclip(0, 10)  # Usa solo los primeros 10 segundos
    text_clip = TextClip(text, fontsize=70, color='white', size=background_clip.size).set_duration(10).set_position('center')
    audio_clip = AudioFileClip(audio_file).subclip(0, 10)
    
    video = CompositeVideoClip([background_clip, text_clip.set_audio(audio_clip)])
    video.write_videofile("output.mp4", fps=24)
