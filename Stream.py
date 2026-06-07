import requests
import logging

logger = logging.getLogger(__name__)

class Stream:
    """
    Handles interactions with the Streamlabs TikTok API.
    """
    def __init__(self, token):
        """
        Initializes the Stream instance with an OAuth token.

        Args:
            token (str): The Streamlabs OAuth token.
        """
        self.s = requests.session()
        self.s.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) StreamlabsDesktop/1.17.0 Chrome/122.0.6261.156 Electron/29.3.1 Safari/537.36",
            "authorization": f"Bearer {token}"
        })

    def search(self, game):
        """
        Searches for a game category on TikTok.

        Args:
            game (str): The game name or category to search for.

        Returns:
            list: A list of matching categories.
        """
        if not game:
            return []
        game = game[:25] # If the game name exceeds 25 characters, the API will return error 500
        url = f"https://streamlabs.com/api/v5/slobs/tiktok/info?category={game}"
        info = self.s.get(url).json()
        info["categories"].append({"full_name": "Other", "game_mask_id": ""})
        return info["categories"]

    def start(self, title, category, audience_type='0'):
        """
        Starts a TikTok live stream.

        Args:
            title (str): The title of the stream.
            category (str): The game mask ID of the category.
            audience_type (str): '0' for general, '1' for mature content.

        Returns:
            tuple: (rtmp_url, stream_key) if successful, (None, None) otherwise.
        """
        url = "https://streamlabs.com/api/v5/slobs/tiktok/stream/start"
        files=(
            ('title', (None, title)),
            ('device_platform', (None, 'win32')),
            ('category', (None, category)),
            ('audience_type', (None, audience_type)),
        )
        response = self.s.post(url, files=files).json()
        try:
            self.id = response["id"]
            return response["rtmp"], response["key"]
        except KeyError:
            logger.error(f"Error starting stream: {response}")
            return None, None

    def end(self):
        """
        Ends the current TikTok live stream.

        Returns:
            bool: True if successful, False otherwise.
        """
        url = f"https://streamlabs.com/api/v5/slobs/tiktok/stream/{self.id}/end"
        response = self.s.post(url).json()
        return response["success"]
    
    def getInfo(self):
        """
        Retrieves information about the user's TikTok account and stream status.

        Returns:
            dict: The API response containing account and status info.
        """
        url = "https://streamlabs.com/api/v5/slobs/tiktok/info"
        response = self.s.get(url).json()
        return response