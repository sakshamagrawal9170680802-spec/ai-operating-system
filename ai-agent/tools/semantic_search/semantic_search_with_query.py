from pathlib import Path

from langchain_core.tools import tool

from tools.semantic_search.folder_reader import get_files
from tools.semantic_search.chunk_creator import chunk_file
from tools.semantic_search.vector_store import create_vector_store


@tool
def semantic_file_search(folder_path: str, query: str) -> dict:
    """
    Search files inside a folder using semantic similarity.

    The folder is scanned recursively, its supported files are
    converted into chunks, stored in a vector database, and the
    most relevant files and content are returned for the query.
    """

    try:
        # 1. Get all files from the folder
        files = get_files(folder_path)

        if not files:
            return {
                "success": False,
                "message": "No files found in the provided folder."
            }

        # 2. Create chunks from the files
        documents = chunk_file(files)

        if not documents:
            return {
                "success": False,
                "message": "No readable content found in the files."
            }

        # 3. Create the vector store
        vector_store = create_vector_store(documents)

        # 4. Search for the query
        results = vector_store.similarity_search_with_score(query,k=20)

        # 5. Group results by file
        file_results = {}

        for document, score in results:

            file_path = document.metadata["source"]

            if file_path not in file_results:
                file_results[file_path] = {
                    "path": str(Path(file_path).resolve()),
                    "filename": Path(file_path).name,
                    "score": score,
                    "relevant_content": []
                }

            file_results[file_path]["relevant_content"].append(document.page_content)

            # Keep the best score for the file
            if score < file_results[file_path]["score"]:
                file_results[file_path]["score"] = score

        # 6. Rank files
        ranked_files = sorted(
            file_results.values(),
            key=lambda x: x["score"]
        )

        # 7. Return top 5 files
        ranked_files = ranked_files[:5]

        return {
            "success": True,
            "query": query,
            "results": ranked_files
        }

    except Exception as e:

        return {
            "success": False,
            "message": f"Semantic search failed: {e}"
        }