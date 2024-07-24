from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import chromadb

class Chroma_DB:
    def __init__(self):
            self.is_initialized = False
            self.langchain_chroma = None
            self.embeddings = None
            self.set_embeddings()

    def set_embeddings(self):
        model_name = "./data/gte-large-en-v1.5"
        model_kwargs = {'device': "cuda", "trust_remote_code": True}
        encode_kwargs = {'normalize_embeddings': False}
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
    )

    def load_documents(self, document_path="./data/sources"):
        document_loader = PyPDFDirectoryLoader(document_path)
        return document_loader.load()
    
    def load_documents_uns(self, document_path="./data/sources"):
        document_loader = UnstructuredFileLoader(document_path)
        return document_loader.load()

    def split_documents(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def create_langchain_db(self, chunks):
        self.langchain_chroma =  Chroma.from_documents(documents=chunks, embedding=self.embeddings)
        
    def delete_langchain_db(self):
        self.langchain_chroma = None
        self.is_initialized = False
        
    def initialize(self):
        try:
            document = self.load_documents()
            chunks = self.split_documents(document)
            self.create_langchain_db(chunks)
            self.is_initialized = True
            print("document loaded")
        except Exception as e:
            print(f"An error occurred during loading file: {e}")
