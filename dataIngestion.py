from langchain_core.documents import Document
from langchain_chroma import Chroma
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
# import sentence_transformers
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

ROOT_DIR = os.getenv("ROOT_DIR") 

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
collection_name = "NoBrokerDB"
persist_directory = os.path.join(os.getcwd(), 'vectore_DB', 'chroma_langchain_DB')

print(os.getcwd()) 
def create_vdb():
        """Ceate vector Database for RAG"""
        success = 0
        failure = 1
        rVal = failure
        try:
            file_path = os.path.join(ROOT_DIR, 'data', 'ingestionData.csv')
            #  File existence check

            print("vdb", persist_directory)

            if not os.path.exists(file_path):
                print(f"Ingestion file does not exist: {file_path}")
                return failure, None
            
            # Read CSV
            df = pd.read_csv(file_path)

            cnt=1     
            inp_doc_lst = []

            # if os.path.exists(persist_directory):
            #      os.remove(persist_directory) 

            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=persist_directory,
            )  
            # Iterate through each row and create a LangChain Document
            for _, row in df.iterrows():
                inp_text = str(row['description']).replace("'", '"')  # Sanitize quotes

                meta_data = {
                    "id": int(cnt),
                    "City": row['City']
                }

                inp_doc = Document(page_content=inp_text, metadata=meta_data)
                inp_doc_lst.append(inp_doc)
                cnt += 1

            vector_store.add_documents(documents=inp_doc_lst)
            print("len of docs", len(inp_doc_lst))

            rVal=success

        except Exception as e:
             rVal=failure
             vector_store = None
             print(f"Error in create_vdb {e}")
        return rVal, vector_store

if __name__ == '__main__':

    ### Only run once
    ## Un comment to 1st time vectore DB formtaion. 
    # #Generating Vector DB
    rVal, vector_store = create_vdb()
    print("rVal=", rVal)  

    # TESt data-ingestion
    vector_store = Chroma(collection_name=collection_name,
                        embedding_function=embeddings, 
                        persist_directory=persist_directory)

    query = "In mumbai city 2 BHK flat below 3 Cr"

    # ## Test VDB Retrievar 
    # results = vector_store.similarity_search(
    # query,
    # # filter={"City": "Mumbai"},
    # )  

    k = vector_store._collection.count()
    print(f"K - {k}")

    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": vector_store._collection.count()})
    results = retriever.invoke("In mumbai city 2 BHK flat below 3 Cr")

    print("len(results)", len(results),'\n' )

    # for res in results:
    #     print(f"* {res.page_content} [{res.metadata}]")