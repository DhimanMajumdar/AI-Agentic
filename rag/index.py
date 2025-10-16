from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

pdf_path = Path(__file__).parent / "nodejs.pdf"


# Load this file in the python program

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()  # page by page docs


print(docs[12])
