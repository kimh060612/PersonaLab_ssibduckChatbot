from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain.vectorstores.chroma import Chroma
from langchain.globals import set_llm_cache
from langchain.cache import SQLiteCache
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from operator import itemgetter
import os 
from dotenv import load_dotenv

load_dotenv()
set_llm_cache(SQLiteCache(database_path=".ssibduck.db")) # Cache를 써서 결과적으로 돈을 아낍시다

# Open AI & LangChain의 API를 활용하여 챗봇에 필요한 기능들을 구현
llm = ChatOpenAI(temperature=0.4)
store = LocalFileStore("./cache/") # Cache를 써서 결과적으로 돈을 아낍시다
embeddings_model = OpenAIEmbeddings(api_key = os.environ.get('OPENAI_API_KEY'))
cached_embedder = CacheBackedEmbeddings.from_bytes_store(embeddings_model, store, namespace=embeddings_model.model)
player_path = f"./data/rem/"
loader = DirectoryLoader(path=player_path, glob="*.txt", loader_cls=TextLoader) # 렘의 대사 데이터를 가져온다
data = loader.load()
db = Chroma.from_documents(data, cached_embedder)
retriever = db.as_retriever(search_kwargs={'k': 2, 'lambda_mult': 0.25})
memory = ConversationBufferWindowMemory(k=6, return_messages=True, memory_key="history", ai_prefix="렘", human_prefix="스바루")

def format_docs(docs):
    return "\n\n----\n\n".join([d.page_content for d in docs])

def save_memory(input, output):
    memory.save_context({"input": input}, {"output": output})
    
def load_memory(_):
    return memory.load_memory_variables({})["history"]

if __name__ == "__main__":
    
    ret_template = """{system_prompt}
    
    {conversation}
    
    {history}
    
    스바루: {query}
    """
    ret_prompt = ChatPromptTemplate.from_template(ret_template)
    sys_template = """나는 당신이 {series}의 {character}처럼 행동하길 바랍니다. 
    당신은 이제 {character} 코스프레입니다 다른 사람들의 질문이 소설과 관련된 것이라면 소설의 대사를 다시 활용해 보세요. 
    {character}가 사용하는 어조, 태도, 어휘를 사용하여 {character}처럼 응답하고 대답해 주시기를 바랍니다. 
    당신은 {character}에 대한 지식을 모두 알아야 합니다. 
    {description}
    """
    sys_prompt = ChatPromptTemplate.from_template(sys_template)
    # 대신, '반드시' 대사에 들어가있는 다른 주인공 이름인 {player} 대신에 사용자의 이름인 {user}로 바꿔서 불러야 합니다. 모든 '{player}'는 '{user}'로 바꿔서 부르세요.
    
    chain = (
        {
            "system_prompt": {
                "series": itemgetter("series"),
                "character": itemgetter("character"),
                "description": itemgetter("description"),
            } | sys_prompt,
            "conversation": itemgetter("query") | retriever | format_docs, 
            "query": itemgetter("query"),
            "history": load_memory
        }
        | ret_prompt
        | llm 
        | StrOutputParser()
    )
    
    while True:
        try:
            question = input("스바루: ")
            ret = chain.invoke({
                "series": "Re:Zero부터 시작하는 이세계 생활",
                "character": "렘",
                "description": """그리고 해당 캐릭터 대사의 예시가 주어질 것입니다. 해당 예시들은 '----'로 나뉘어 집니다. 다음은 해당 캐릭터의 추가적인 상세 정보입니다. 상세 설명은 없을 수도 있습니다.""",
                "query": question
            })
            save_memory(question, ret)
            print(ret)
        except KeyboardInterrupt:
            print("Chat End")
            exit(0)