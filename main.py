from twitter_api import get_trends
from text_generator import generate_text_with_huggingface
from audio_generator import create_audio
from video_creator import create_video, download_background_video
from youtube_scraper import upload_to_youtube
from tiktok_scraper import upload_to_tiktok

def main():
    """Función principal que coordina todo el proceso de generación y subida de videos."""
    trends = get_trends()
    text = generate_text_with_huggingface(trends)
    create_audio(text, "output.mp3")
    download_background_video("nature", "background.mp4")
    create_video(text, "output.mp3", "background.mp4")
    upload_to_youtube("output.mp4", "Tendencias en Twitter", text)
    upload_to_tiktok("output.mp4", text)

if __name__ == "__main__":
    main()
