from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv
load_dotenv()

question = "내 이름은 나츠키 스바루! 천하 제일 무일푼의 한량이다!"
store = LocalFileStore("./cache/")

if __name__ == "__main__":

    embeddings_model = OpenAIEmbeddings(api_key = os.environ.get('OPENAI_API_KEY'))
    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        embeddings_model, store, namespace=embeddings_model.model
    )
    character_list = os.listdir("./data/")
    character_list.remove("dialogue")
    print(character_list)
    player_path = f"./data/rem/"
    loader = DirectoryLoader(path=player_path, glob="*.txt", loader_cls=TextLoader)
    data = loader.load()
    db = Chroma.from_documents(data, cached_embedder)
    