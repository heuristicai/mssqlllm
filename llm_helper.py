
from langchain_openai import ChatOpenAI

def get_llm():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    return llm
