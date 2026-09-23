from pathlib import Path# helps in opening folder and manging its content

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".docx"
}

def get_files(folder_path:str):
    folder=Path(folder_path)

    if not folder.exists():
        raise ValueError("Folder does not exist")
    if not folder.is_dir():
        raise ValueError("Provided Path is not a folder")

    files=[]

    for file in folder.rglob("*"):
        if file.is_file():
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(str(file.resolve()))
    return files