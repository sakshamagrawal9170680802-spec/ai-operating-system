from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)

def chunk_file(text: str, file_path: str):
    documents = text_splitter.create_documents([text],
        metadatas=[
            {
                "source": file_path,
                "filename": Path(file_path).name
            }
        ]
    )

    return documents
