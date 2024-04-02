import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.globals import set_verbose, set_debug
from chromadb.api.models.Collection import GetResult
import few_shots_helper
set_debug(True)
set_verbose(True)
load_dotenv()


chroma_persist_path = os.environ["CHROMA_PERSIST_PATH"]
vectorstore: Chroma = None
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_vectorstore():
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=chroma_persist_path)
    #Check if this is fresh start 
    get_result: GetResult = vectorstore.get(limit=1)
    if len(get_result['ids']) == 0:
        # Add JSON file to Chroma
        few_shots_df = few_shots_helper.get_few_shots_df()
        few_shots = few_shots_df.to_dict(orient='records')

        index_ids = [str(i) for i in few_shots_df.index.values.tolist()]
        to_vectorize = [example['Question'] for example in few_shots]
        vectorstore.add_texts(texts=to_vectorize, metadatas=few_shots, ids=index_ids)
        vectorstore.persist()   
    return vectorstore

def add_new_items(edited_df):
    index_ids = [str(i) for i in edited_df.index.values.tolist()]
    newitems_dict = edited_df.to_dict(orient='records')
    
    to_vectorize = [example['Question'] for example in newitems_dict]
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=chroma_persist_path)
    ids = vectorstore.get()['ids']
    vectorstore.delete(ids=ids)
    vectorstore.add_texts(texts=to_vectorize, metadatas=newitems_dict, ids=index_ids)
    vectorstore.persist()   

