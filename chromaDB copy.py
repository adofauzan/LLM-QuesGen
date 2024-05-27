from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_chroma import Chroma
import chromadb

class Chroma_DB:
    def __init__(self):
            self.is_initialized = False
            self.client = None
            self.collection = None
            self.langchain_chroma = None
            self.embeddings = None
            self.initialize()

    def initialize(self):
        try:
            self.client = chromadb.PersistentClient(path="./data/chroma_db")
            self.collection = self.client.get_or_create_collection("books")
            model_name = "all-MiniLM-L6-v2.gguf2.f16.gguf"
            gpt4all_kwargs = {'allow_download': 'True'}
            self.embeddings = GPT4AllEmbeddings(
                model_name=model_name,
                gpt4all_kwargs=gpt4all_kwargs
                )
            self.langchain_chroma = Chroma(client=self.client, collection_name="books", embedding_function = self.embeddings)
            self.is_initialized = True
            print("vector_db is initalized")
        except Exception as e:
            print(f"An error occurred during initialization: {e}")

    def load_documents(self, document_path="./data/sources"):
        document_loader = PyPDFDirectoryLoader(document_path)
        return document_loader.load()

    def split_documents(self, documents: list[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)

    def add_to_chroma(self, chunks):
        page_contents = []
        metadatas = []
        ids = [str(i) for i in range(1, len(chunks) + 1)]

        for doc in chunks:
            page_contents.append(doc.page_content)
            metadatas.append(doc.metadata)

        self.collection.upsert(
            ids=ids,
            documents=page_contents, 
            metadatas=metadatas
        )

    def update_langchain_chroma(self):
        self.langchain_chroma = Chroma(client=self.client, collection_name="books", embedding_functions = embeddings)

    def update_collection(self):
        docs = self.load_documents()
        chunks = self.split_documents(docs)
        self.add_to_chroma(chunks)
        self.update_langchain_chroma()
