from langchain.document_loaders import PyPDFLoader,TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
import os
from tqdm import tqdm

DATA_PATH = "C:/Users/KAAN/Desktop/Data"
CHROMA_PATH = "Lotr_Database"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"



if not os.path.exists(CHROMA_PATH):
    os.makedirs(CHROMA_PATH)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="lotr_data")


embedding_model = SentenceTransformer(EMBEDDING_MODEL)

documents = []
print("Dosyalar yükleniyor...")
for file_name in tqdm(os.listdir(DATA_PATH), desc="Dosya Yükleme"):
    file_path = os.path.join(DATA_PATH, file_name)
    try:
        if file_name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif file_name.endswith(".txt"):
            loader = TextLoader(file_path)
            documents.extend(loader.load())
    except Exception as e:
        print(f"Hata oluştu: {file_name} atlanıyor. Hata: {e}")

print(f"Toplam {len(documents)} belge yüklendi.")


if not documents:
    raise ValueError("Hiç .pdf dokümanı yüklenemedi. Veri yolunu ve .pdf dosyalarını kontrol edin.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=300,
)

print("Chunklara ayrılıyor...")
chunks = list(tqdm(text_splitter.split_documents(documents), desc="Chunking"))
print(f"{len(chunks)} adet chunk başarıyla oluşturuldu.")

if not chunks:
    raise ValueError("Dokümanlar parçalanamadı. Text splitter parametrelerini kontrol edin.")

chunk_contents = []
metadata = []
ids = []

print("Chunk içerikleri hazırlanıyor...")
for i, chunk in tqdm(enumerate(chunks), total=len(chunks), desc="Chunk Processing"):
    if not chunk.page_content.strip():
        continue
    chunk_contents.append(chunk.page_content)
    ids.append(f"ID{i}")
    metadata.append(chunk.metadata)

if not chunk_contents:
    raise ValueError("Hiçbir geçerli içerik bulunamadı. Parçalanan içerikleri kontrol edin.")

print(f"{len(chunk_contents)} adet geçerli chunk hazırlandı.")

try:
    print("Embedding'ler oluşturuluyor...")
    embeddings = embedding_model.encode(
        chunk_contents, convert_to_numpy=True, show_progress_bar=True
    )
    print(f"{len(embeddings)} embedding başarıyla oluşturuldu.")
except Exception as e:
    raise RuntimeError(f"Embedding oluşturma sırasında hata oluştu: {e}")

try:
    print("ChromaDB'ye veri ekleniyor...")
    for start in tqdm(range(0, len(chunk_contents), 100), desc="Veri Ekleniyor"):
        end = start + 100
        collection.add(
            documents=chunk_contents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadata[start:end],
            ids=ids[start:end]
        )
    print(f"{len(ids)} içerik başarıyla ChromaDB'ye eklendi.")
except Exception as e:
    raise RuntimeError(f"ChromaDB'ye ekleme sırasında hata oluştu: {e}")