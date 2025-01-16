# Palantír AI - Lord of the Rings RAG Chatbot

Palantír AI is an intelligent chatbot system that leverages RAG (Retrieval-Augmented Generation) technology to provide accurate and contextual answers about J.R.R. Tolkien's works, particularly The Lord of the Rings and related writings. The system combines document retrieval, natural language processing, and Google's Gemini AI to create an engaging conversational experience.

## Features

- **RAG-based Knowledge System**: Uses ChromaDB for efficient document storage and retrieval
- **Multi-modal Interaction**: Supports both text and voice input/output
- **Image Integration**: Automatically fetches relevant images for queries using Google Custom Search API
- **User Authentication**: Secure Firebase-based user authentication system
- **Chat History**: Persistent storage of conversation history using Firestore
- **Multilingual Support**: Handles queries in multiple languages through Google Translator
- **Voice Interface**: Speech-to-text and text-to-speech capabilities

## Technical Architecture

### Backend Components
- FastAPI server for API endpoints
- ChromaDB for vector database
- Google Gemini AI for natural language generation
- Firebase Authentication and Firestore for user management
- Google Custom Search API for image retrieval

### Frontend Components
- Streamlit web interface
- Audio recording and playback capabilities
- Real-time chat interface
- Chat history management

## Setup Instructions

1. **Environment Setup**
```bash
pip install -r requirements.txt
```

2. **Environment Variables**
Create a `.env` file with the following:
```
GEMINI_API_KEY=your_gemini_api_key
API_KEY=your_google_api_key
CX=your_google_custom_search_cx
```

3. **Firebase Configuration**
- Place your Firebase credentials JSON file in the project root
- Update the path in the code to match your credentials file name

4. **Database Setup**
```python
python vector_database.py
```

5. **Running the Application**
```bash
# Start the FastAPI server
uvicorn api:app --reload

# Start the Streamlit interface
streamlit run app.py
```

## Project Structure

```
project/
├── api.py              # FastAPI backend server
├── app.py              # Streamlit frontend
├── vector_database.py      # Document processing and database setup
├── pages/
│   └── login.py       # Authentication interface
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## API Endpoints

- `POST /ask`: Process user queries and generate responses
- `GET /get-image`: Fetch relevant images for queries

## Dependencies

Core dependencies include:
- fastapi
- streamlit
- firebase-admin
- chromadb
- google-generativeai
- sentence-transformers
- deep-translator
- gtts
- SpeechRecognition

## Features in Detail

### Document Processing
- Supports PDF and TXT file processing
- Implements chunk-based document splitting
- Uses sentence transformers for embedding generation

### User Interface
- Clean, intuitive chat interface
- Real-time response generation
- Voice input/output capabilities
- Image display integration
- Chat history management

### Authentication
- Email/password-based authentication
- Secure session management
- User-specific chat history

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- J.R.R. Tolkien's works
- Google Gemini AI
- ChromaDB team
- Firebase team
- Streamlit community

## Results 

![image](https://github.com/user-attachments/assets/666db6d8-0c41-4d29-852d-e9ac684e7908)

![image](https://github.com/user-attachments/assets/b4be7335-5e39-4730-910f-8b544c94e074)

![image](https://github.com/user-attachments/assets/227fb158-8c62-43ba-a1ef-ee63c3e2e2f9)




## Contact

For questions and support, please open an issue in the GitHub repository.

---
**Note**: This project is a fan-made application and is not officially associated with the Tolkien Estate or any related entities.
