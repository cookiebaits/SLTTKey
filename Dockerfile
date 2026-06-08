FROM python:3.11-slim

# Install system dependencies for PySide6 and X11
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for headless environments or X11 forwarding
# NOTE: This is a GUI application. Running in a standard Docker container
# will require an X11 server on the host or a VNC/RDP setup.
ENV QT_QPA_PLATFORM=offscreen

CMD ["python", "StreamLabsTikTokStreamKeyGenerator.py"]
