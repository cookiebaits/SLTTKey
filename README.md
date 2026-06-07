# TikTok Live Stream Key Generator for OBS Studio Using Streamlabs API

## Description
This application is a simple tool that generates a TikTok Live Stream Key for OBS Studio using the Streamlabs API. It features a modern, dark-themed UI and follows best practices for security and maintainability.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/loukious)


## Features
- **Modern UI/UX:** Polished dark-themed interface with optimized layouts.
- **Secure Token Handling:** Utilizes PKCE (Proof Key for Code Exchange) for OAuth and avoids sensitive data leaks.
- **Local & Web Login:** Load tokens directly from Streamlabs Desktop or through a browser login.
- **Game Search:** Easily search and select TikTok game categories.
- **Auto-Update:** Built-in version checker to stay up to date.

## Requirements
- Streamlabs TikTok LIVE access. You can request access [here](https://tiktok.com/falcon/live_g/live_access_pc_apply/result/index.html?id=GL6399433079641606942&lang=en-US)
- TikTok account
- Streamlabs installed on your computer (optional for "Load from PC")

## Security
This application is built with security in mind:
- **No Token Leaks:** Tokens are never logged to console or stdout.
- **PKCE:** Uses secure OAuth flow to protect your credentials.
- **Validation:** All inputs and tokens are validated before use.

## Deployment

### Standard Deployment (Ubuntu/Standard OS)
1. Install requirements: `pip install -r requirements.txt`
2. Run the app: `python StreamLabsTikTokStreamKeyGenerator.py`

### Docker Deployment via Dokploy
The project includes a `Dockerfile` and `docker-compose.yml` for easy deployment in containerized environments.

1. **Build and Start:**
   ```bash
   docker-compose up -d --build
   ```
2. **X11 Forwarding:** The container is configured for X11 forwarding. Ensure your host system has an X server running (like XQuartz on macOS or native X11 on Linux).

## Network Ports
- **OAuth Callback:** The application utilizes a random ephemeral port on `127.0.0.1` for the OAuth callback during "Login from Web". Ensure your firewall allows local loopback traffic.

## Usage
1. Run the application.
2. Click on the "Load from PC" button if you have Streamlabs installed, otherwise click on "Login from Web".
3. Select stream title and category.
4. Click on "Save Config" button.
5. Click on "Go Live" button.

## Screenshots
![Modern UI](https://i.imgur.com/2PSgEQP.png)

## Checkout my OBS-Multi-RTMP plugin fork!
With [this](https://github.com/Loukious/obs-multi-rtmp) plugin, you can use your streamlabs token to stream directly to TikTok by saving it only once.

## FAQ
### I'm getting an error when I try to stream. What should I do?
1. First make sure it's not an issue related to Streamlabs. Try going live using Streamlabs and see if you get the same error.
2. Check `app.log` for detailed error messages.
3. If it's not an issue related to Streamlabs, create an issue on GitHub.
