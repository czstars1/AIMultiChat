from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from src.myproject.config import DATA_DIR

db_path = DATA_DIR / "chroma_db"

client = PersistentClient(path=str(db_path))

collection = client.get_or_create_collection(name="knowledge_base")

model = SentenceTransformer('all-MiniLM-L6-v2')