import requests
import streamlit as st
import datetime
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials, auth
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import os
import base64
import speech_recognition as sr
import json


API_URL = "http://127.0.0.1:8000/ask"
IMAGE_API_URL = "http://127.0.0.1:8000/get-image"



st.set_page_config(page_title="Palantír AI")
st.title("Palantír AI")

firebase_config=st.secrets["firebase_config"]

file_path = "firebase_config.json"


with open(file_path, "w") as json_file:
    json.dump(firebase_config, json_file, indent=4)

if not firebase_admin._apps:
    cred = credentials.Certificate(file_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def save_chat_to_firestore(username, chat_id, messages):
    doc_ref = db.collection("users").document(username).collection("chats").document(chat_id)
    doc_ref.set({"messages": messages})
    
def load_user_chats(username):
    chat_histories = {}
    chats_ref = db.collection("users").document(username).collection("chats")
    for chat_doc in chats_ref.stream():
        chat_histories[chat_doc.id] = chat_doc.to_dict()["messages"]
    return chat_histories

if "username" in st.session_state:
    username = st.session_state["username"]
    st.session_state["chat_histories"] = load_user_chats(username)
    st.write(f"Merhaba {username}, Middle-earth hakkında ne öğrenmek istersiniz?")
else:
    st.warning("Lütfen giriş yapın.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "chat_histories" not in st.session_state:
    st.session_state["chat_histories"] = {}
if "current_chat" not in st.session_state:
    st.session_state["current_chat"] = None
    

 
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Konuşmaya başlayabilirsiniz...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="tr-TR")
            st.success(f"Saptanan metin: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Ses anlaşılamadı, lütfen tekrar deneyin.")
        except sr.RequestError as e:
            st.error(f"Ses tanıma servisiyle ilgili bir sorun oluştu: {e}")
        return None
    
    
def play_response_text(response_text, lang="tr"):
    tts = gTTS(text=response_text, lang=lang)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")
    os.remove("response.mp3")

     
st.sidebar.title("Chat History")


button_container = st.sidebar.container()
col1, col2 = button_container.columns([1, 1])


with col1:
    new_chat_button = st.button("New Chat", use_container_width=True)
    
with col2:
    logout_button = st.button("Log out", use_container_width=True)
    
if new_chat_button:
    new_chat_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["chat_histories"][new_chat_id] = []
    st.session_state["current_chat"] = new_chat_id
    st.session_state["messages"] = []
    st.rerun()

if logout_button:
    st.session_state.clear()
    st.switch_page("pages/login.py")
    
sorted_chat_histories = sorted(st.session_state["chat_histories"].items(), key=lambda x: x[0], reverse=True)

for chat_id, chat_history in sorted_chat_histories:
    with st.sidebar.container():
        # Display the chat preview
        user_query_preview = chat_history[0]["content"] if chat_history else "Yeni Sohbet"
        if not isinstance(user_query_preview, str):
            user_query_preview = str(user_query_preview)
        
        col1, col2 = st.columns([4, 1])  
        with col1:
            if st.button(user_query_preview, key=chat_id):
                st.session_state["current_chat"] = chat_id
                st.session_state["messages"] = chat_history
                st.rerun()
        
        with col2:
           
            if st.button("🗑️", key=f"delete_{chat_id}"): 
                
                db.collection("users").document(username).collection("chats").document(chat_id).delete()
                
                
                st.session_state["chat_histories"].pop(chat_id, None)
                
                
                if st.session_state["current_chat"] == chat_id:
                    st.session_state["current_chat"] = None
                    st.session_state["messages"] = []
                
                st.rerun()
    


    
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("image"):
            st.image(message["image"])

recorded_audio=audio_recorder()      

if user_query := st.chat_input("Soru yazın ve Enter'a basın..."):
    with st.chat_message("user"):
        st.write(user_query)
    st.session_state["messages"].append({"role": "user", "content": user_query})

    try:
        
        response = requests.post(API_URL, json={"question": user_query})
        response_data = response.json()

        assistant_response = response_data.get("response", "Maalesef, sorunuza bir yanıt veremedim.")
        with st.chat_message("assistant"):
            st.write("**Yanıt:**")
            st.write(assistant_response)
            
        

        image_response = requests.get(IMAGE_API_URL, json={"question": user_query})
        if image_response.status_code == 200:
            img = image_response.content
            st.image(img, caption="Image related to your query", use_column_width=True)
            st.session_state["messages"].append({"role": "assistant", "content": assistant_response, "image": image_response.content})
        else:
            st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
            
        if st.session_state["current_chat"]:
            st.session_state["chat_histories"][st.session_state["current_chat"]] = st.session_state["messages"]
            save_chat_to_firestore(username, st.session_state["current_chat"], st.session_state["messages"])
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}") 
        


elif recorded_audio:
    audio_file="audio.mp3"
    with open(audio_file, "wb") as f:
        f.write(recorded_audio)
    user_query = recognize_speech()
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
        st.session_state["messages"].append({"role": "user", "content": user_query})
        try:
        
            response = requests.post(API_URL, json={"question": user_query})
            response_data = response.json()

            assistant_response = response_data.get("response", "Maalesef, sorunuza bir yanıt veremedim.")
            with st.chat_message("assistant"):
                st.write("**Yanıt:**")
                st.write(assistant_response)
                play_response_text(assistant_response)
                
            

            image_response = requests.get(IMAGE_API_URL, json={"question": user_query})
            if image_response.status_code == 200:
                img = image_response.content
                st.image(img, caption="Image related to your query", use_column_width=True)
                st.session_state["messages"].append({"role": "assistant", "content": assistant_response, "image": image_response.content})
            else:
                st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
                
            if st.session_state["current_chat"]:
                st.session_state["chat_histories"][st.session_state["current_chat"]] = st.session_state["messages"]
                save_chat_to_firestore(st.session_state["current_chat"], st.session_state["messages"])
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}") 
