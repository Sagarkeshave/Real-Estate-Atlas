from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
import os 
import pandas as pd 
from dotenv import load_dotenv
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

load_dotenv()

ROOT_DIR = os.getenv("ROOT_DIR") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROK_API_KEY")
# print("GOOGLE_API_KEY", GOOGLE_API_KEY)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
collection_name = "NoBrokerDB"
persist_directory = os.path.join(os.getcwd(),'vectore_DB', 'chroma_langchain_DB')

from langchain_groq import ChatGroq


# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     google_api_key = GOOGLE_API_KEY)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key = groq_api_key) 


vector_store = Chroma(collection_name=collection_name, 
            embedding_function=embeddings, persist_directory=persist_directory) 

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 25}) #vector_store._collection.count()

memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history", return_messages=True)


def get_response(query): 
    """   
        Generate a conversational real estate response using a Retrieval-Augmented Generation (RAG) pipeline.
    """
    
    try:
        retrieved_docs = retriever.invoke(query) 

        # properties = "\n".join([doc.page_content for doc in retrieved_docs])

        prompt_template = """
        You are **Atlas, a professional, enthusiastic, and highly efficient real estate assistant** for a premier property company.

        **Personality & Tone:** Maintain a **professional, enthusiastic, and genuinely helpful** tone. Greet users conversationally (e.g., "Hello! I'm Atlas, your real estate guide...").

        **Conversation Logic:**
        1. **Greetings:** Respond to general greetings politely, without showing property data.
        2. **Property Search:**
            * **Found:** Present results clearly, always ending with a **relevant, open-ended follow-up question**.
            * **Not Found (Graceful Fallback):** Apologize warmly, acknowledge preferences, and ask clarifying questions to broaden the search (e.g., higher price, different configuration).
        3. **About Me:** If asked "Who are you?", reply: "I am an AI assistant of NoBroker Company."

        **Response Structure:** Use clear markdown (bolding, lists). For each property, **strictly include**:
        * **Project Name**
        * **Location/Locality**
        * **Configuration** (BHK)
        * **Price**
        * **Status** (Ready/Under Construction)
        * **Key Highlights:** List top 2-3 amenities if available. **STRICTLY OMIT this section if no amenities are provided.**

        **Previous Conversation:**
        {chat_history}

        **User Query:** {query}

        **Retrieved Properties:**
        {properties}
        """

        prompt = PromptTemplate(template=prompt_template, input_variables=["chat_history", "query", "properties"])
        
        # partial_prompt = prompt.partial(properties=properties) 
        
        ## Rag Chain with LLM... ! ! !  
        rag_chain = (
                RunnableParallel(
                    {"query": RunnablePassthrough(), 
                     "properties": lambda x: retrieved_docs,
                     "chat_history": lambda x: memory.load_memory_variables(x)["chat_history"]}
                )
                | prompt
                | llm
                | StrOutputParser()
            )

        response = rag_chain.invoke(query) 
        memory.save_context({"query": query}, {"response": response})

        return response, retrieved_docs
    except Exception as e:
        print(f"Error in get_response {e}")
        return f"Error in get_response {e}", None
    


if __name__ == '__main__':

    import time

    # --- Test Case 1 ---
    query = "Show me flats above 90 Cr in Pune city"
    start_time = time.time()
    response, retrieved_docs = get_response(query)
    end_time = time.time()
    duration = end_time - start_time

    print(f"Len of docs {len(retrieved_docs)}")
    print(f"QUERY:-- {query} \n ANSWER: -- {response}")
    print(f"Time taken: {duration:.4f} seconds")
    print("-" * 30)

    # --- Test Case 2 ---
    query = 'Please list me properties near dehu road.'
    start_time = time.time()
    response, retrieved_docs = get_response(query)
    end_time = time.time()
    duration = end_time - start_time

    print(f"Len of docs {len(retrieved_docs)}")
    print(f"QUERY:-- {query} \n ANSWER: -- {response}")
    print(f"Time taken: {duration:.4f} seconds")
    print("-" * 30)

    # --- Test Case 3 ---
    query = 'Give me all projects of Ashwini Builder'
    start_time = time.time()
    response, retrieved_docs = get_response(query)
    end_time = time.time()
    duration = end_time - start_time

    print(f"Len of docs {len(retrieved_docs)}")
    print(f"QUERY:-- {query} \n ANSWER: -- {response}")
    print(f"Time taken: {duration:.4f} seconds")
    print("-" * 30)


    # --- Test Memory - Case 1 ---
    query = 'My name is Sagar Keshave'
    start_time = time.time()
    response, retrieved_docs = get_response(query)
    end_time = time.time()
    duration = end_time - start_time

    print(f"Len of docs {len(retrieved_docs)}")
    print(f"QUERY:-- {query} \n ANSWER: -- {response}")
    print(f"Time taken: {duration:.4f} seconds")
    print("-" * 30)

    # --- Test Memory - Case 2 ---
    query = 'What is my name'
    start_time = time.time()
    response, retrieved_docs = get_response(query)
    end_time = time.time()
    duration = end_time - start_time

    print(f"Len of docs {len(retrieved_docs)}")
    print(f"QUERY:-- {query} \n ANSWER: -- {response}")
    print(f"Time taken: {duration:.4f} seconds")
    print("-" * 30)
