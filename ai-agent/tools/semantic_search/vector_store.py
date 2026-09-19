from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings=HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")

CHROMA_PATH = "./chroma_db"

def create_vector_store(documents):
    vector_store=Chroma(collection_name="aegis_documents",
                        embedding_function="embeddings",
                        persist_directory=CHROMA_PATH)

    vector_store.add_documents(documents)

    return vector_store