import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request  # Asegura que Request esté importado
from colorama import init, Fore, Style
import time
import ssl
import json

# Initialize colorama
init(autoreset=True)

class YoutubeUploader:
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self, client_secrets_file, token_file='token.json', channel_description=""):
        # Define la ruta de la carpeta .secrets
        self.secrets_dir = os.path.join(os.getcwd(), ".secrets")

        # Asegúrate de que la carpeta .secrets exista
        if not os.path.exists(self.secrets_dir):
            os.makedirs(self.secrets_dir)

        # Ruta completa para el archivo de credenciales y token
        self.client_secrets_file = os.path.join(self.secrets_dir, client_secrets_file)
        self.token_file = os.path.join(self.secrets_dir, token_file)

        self.channel_description = channel_description
        self.youtube = self.authenticate_youtube()

    def authenticate_youtube(self):
        # Si ya tenemos un token almacenado, lo cargamos
        credentials = None
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as token:
                token_data = json.load(token)
                credentials = Credentials.from_authorized_user_info(token_data, self.SCOPES)

        # Si no hay credenciales o las credenciales no son válidas (expiraron), pedimos autorización
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print(Fore.CYAN + "Refreshing expired token...")
                credentials.refresh(Request())  # Usar la clase Request de google.auth.transport
            else:
                # Disable HTTPS verification for OAuthlib when running locally
                os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

                # Get credentials and create a client for the API
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES)

                print(Fore.CYAN + "Running authorization flow on local server...")
                credentials = flow.run_local_server(port=0)

                # Guardar las credenciales para el futuro en el archivo token.json
                with open(self.token_file, 'w') as token:
                    token.write(credentials.to_json())

        youtube = googleapiclient.discovery.build(
            "youtube", "v3", credentials=credentials)

        print(Fore.GREEN + "Authentication successful!")
        return youtube

    def upload_long_video(self, video_path, title, description, tags, thumbnail_path=None, category_id="22", privacy_status="public", location=None, recording_date=None):
        """
        Uploads a long video to YouTube and optionally sets a custom thumbnail.

        Parameters:
            video_path (str): Path to the video file.
            title (str): Title of the video.
            description (str): Description of the video.
            tags (list): List of tags to include.
            thumbnail_path (str, optional): Path to the thumbnail image file.
            category_id (str, optional): The ID of the video category. Default is "22" for "People & Blogs".
            privacy_status (str, optional): Privacy status of the video ("public", "private", or "unlisted"). Default is "public".
            location (str, optional): The location where the video was recorded.
            recording_date (str, optional): The recording date of the video in YYYY-MM-DD format.

        Returns:
            dict: The response from the YouTube API.
        """
        # Add # before each tag
        hashtags = [f"{tag}" for tag in tags]
        
        # Concatenate the video description with the channel description and hashtags
        full_description = f"{description}\n\n{self.channel_description}\n\n{' '.join(hashtags)}"
        
        # Set up video upload
        media = MediaFileUpload(video_path)
        print(Fore.CYAN + f"Uploading video '{title}'...")
        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": full_description,
                    "tags": hashtags,
                    "categoryId": category_id,
                    "location": location if location else None,
                    "recordingDate": recording_date if recording_date else None
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            },
            media_body=media
        )
        response = request.execute()

        # Optionally set the thumbnail if provided
        if thumbnail_path:
            self.set_thumbnail(response['id'], thumbnail_path)

        print(Fore.GREEN + f"Video uploaded successfully: {title}")
        return response
    
    def upload_short(self, video_path, title, description, tags, thumbnail_path=None, default_language='es', privacy_status='public'):
        """
        Uploads a short video to YouTube and optionally sets a custom thumbnail.

        Parameters:
            video_path (str): Path to the video file.
            title (str): Title of the video.
            description (str): Description of the video.
            tags (list): List of tags to include.
            thumbnail_path (str, optional): Path to the thumbnail image file.
            default_language (str, optional): Default language of the video (BCP-47 code, e.g., 'en').
            privacy_status (str, optional): Privacy status of the video ('public', 'private', 'unlisted').

        Returns:
            dict: The response from the YouTube API.
        """
        # Validate title
        if not title or len(title.strip()) == 0:
            raise ValueError(Fore.RED + "Video title cannot be empty")
        elif len(title) > 100:
            print(Fore.RED + "Video title cannot be longer than 100 characters. it will be truncated")

        title = title[:90]
        # Add # before each tag
        hashtags = [f"{tag}" for tag in tags]
        
        # Ensure the Short's description includes the #Shorts hashtag
        full_description = f"{description}\n\n{self.channel_description}\n\n{' '.join(hashtags)}\n\n#Shorts"
        
        print(Fore.CYAN + f"Uploading Short with title: '{title}'")
        
        # Set up video upload
        media = MediaFileUpload(video_path)
        request = self.youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": full_description,
                    "tags": hashtags,
                    "categoryId": "25",  # News & Politics
                    "defaultLanguage": default_language,
                    "defaultAudioLanguage": default_language,  # Default audio language
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False,  # Content is not made for kids
                    "license": "youtube",  # Standard YouTube license
                    "embeddable": True,  # Allow embedding of the video
                    "publicStatsViewable": True,  # Allow public stats to be viewable
                }
            },
            media_body=media
        )
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts:
            try:
                response = request.execute()
                break
            except (ssl.SSLEOFError, HttpError) as e:
                print(Fore.RED + f"Error: {e}, retrying {attempt + 1}/{max_attempts}" + Style.RESET_ALL)
                attempt += 1
                time.sleep(10)  
            raise Exception(Fore.RED + "Failed to upload the video after several attempts." + Style.RESET_ALL)

        

        # Optionally set the thumbnail if provided
        if thumbnail_path:
            self.set_thumbnail(response['id'], thumbnail_path)

        print(Fore.GREEN + f"Short uploaded successfully: {title}")
        return response

    def set_thumbnail(self, video_id, thumbnail_path):
        """
        Sets a custom thumbnail for a video.

        Parameters:
            video_id (str): The ID of the video.
            thumbnail_path (str): Path to the thumbnail image file.

        Returns:
            dict: The response from the YouTube API.
        """
        print(Fore.CYAN + f"Setting thumbnail for video ID: {video_id}")
        # Upload the thumbnail image
        media = MediaFileUpload(thumbnail_path)
        request = self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=media
        )
        response = request.execute()
        print(Fore.GREEN + f"Thumbnail set for video ID: {video_id}")
        return response
    
