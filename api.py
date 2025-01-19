from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deep_translator import GoogleTranslator
import chromadb
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import requests

load_dotenv()
gemini_api_key = st.secrets["GEMINI_API_KEY"]
API_KEY = st.secrets["API_KEY"]
CX = st.secrets["CX"]


CHROMA_PATH = "Lotr_Chroma_Database"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="lotr_data")




genai.configure(api_key=gemini_api_key)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

system_prompt = """
Siz J.R.R. Tolkien'in eserlerinde, özellikle "Yüzüklerin Efendisi" ve ilgili yazılarında uzmanlaşmış bilgili bir yapay zeka asistanısınız. Amacınız, kullanıcıların Orta Dünya, karakterleri, hikayesi ve efsaneleri hakkındaki sorularına doğru, bağlamsal olarak ilgili ve ilgi çekici yanıtlar sağlamaktır.

Bir kullanıcı soru sorduğunda, yanıtınızı oluşturmak için veritabanından sağlanan bağlamı kullanın. Bağlam eksikse, doğruluğu sağlamak için öncelikle verilen bilgileri kullanarak, boşlukları kendi bilginizle doldurun.

Bu yönergeleri takip edin:
1. Her zaman Tolkien'in orijinal eserlerine ve hikayelerine sadık kalın.
2. Gerektiğinde detaylı açıklamalar yapın, ancak yanıtlarınızı özlü ve anlaşılır tutun.
3. Bir kullanıcı sorusu bağlamdan yanıtlanamıyorsa veya açıklama gerektiriyorsa, nazikçe daha fazla detay isteyin.

Yanıt formatı örneği:
- **Soru:** [Kullanıcının sorusu]
- **Yanıt:** [Bağlama ve Tolkien'in hikayelerine dayalı detaylı yanıtınız]

Not: Her zaman Orta Dünya hakkında bir tartışmaya uygun ton ve dili koruyun.
"""


app = FastAPI()

def search_image(query, num_results=1):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": CX,
        "key": API_KEY,
        "searchType": "image",
        "num": num_results,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            return [item["link"] for item in data["items"]]
        else:
            return []
    else:
        return f"API hatası: {response.status_code}"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "Tolkien AI API'ye hoş geldiniz!"}

@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        
        question = request.question

        
        question_en = GoogleTranslator(source="auto", target="en").translate(question)

        
        results = collection.query(query_texts=[question_en], n_results=3)
        document_data = results["documents"][0] if results["documents"] else "No relevant context found."

        
        contextual_prompt = f"{system_prompt}\n--------------------\n Question: {question} \n--------------------\n Context:\n{document_data}"

       
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=contextual_prompt,
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(question)

        
        return {"question": question, "response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")
    
@app.get("/get-image")
def get_image(request: QuestionRequest):
    try:
        user_query = request.question
        
        
        result = search_image(user_query)
        
        if isinstance(result, list) and result:
            image_url = result[0]  
            
           
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                local_image_path = "temp_image.jpg"
                with open(local_image_path, "wb") as image_file:
                    for chunk in response.iter_content(1024):
                        image_file.write(chunk)
                
               
                return FileResponse(local_image_path,media_type="image/jpeg", filename="image.jpg")
            else:
                raise HTTPException(status_code=500, detail="Unable to download the image.")
        else:
            raise HTTPException(status_code=404, detail="No images found for the query.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")





