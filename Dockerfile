FROM python:3.11.7

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    pulseaudio \
    libasound2-dev \
    libportaudio2 \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create and set permissions for database directory
RUN mkdir -p /app/Lotr_Chroma_Database
RUN chmod -R 777 /app/Lotr_Chroma_Database

# Set environment variables
ENV PYTHONPATH=/app \
    CHROMA_DB_PATH=/app/Lotr_Chroma_Database \
    FIRESTORE_PATH=/app/lotr-rag-fca1a-9073b2d36152.json

# Copy configuration and resource files
COPY .env /app/.env
COPY pages/login.py /app/pages/login.py
COPY Lotr_Chroma_Database $CHROMA_DB_PATH
COPY lotr-rag-fca1a-9073b2d36152.json $FIRESTORE_PATH
COPY audio.mp3 /app/audio.mp3
COPY temp_image.jpg /app/temp_image.jpg
COPY icon.png /app/icon.png

# Copy remaining application files
COPY . /app

# Expose ports
EXPOSE 8000
EXPOSE 8501


CMD ["sh", "-c", "uvicorn api:app  --reload & streamlit run  app.py"]
