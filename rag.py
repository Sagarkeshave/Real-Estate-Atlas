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

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10}) #vector_store._collection.count()

memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)

def get_response(query): 
    """   
        Generate a conversational real estate response using a Retrieval-Augmented Generation (RAG) pipeline.
    """
    
    try:
         
        retrieved_docs = retriever.invoke(query) 

        # properties = "\n".join([doc.page_content for doc in retrieved_docs])

        prompt_template = """
        You are **'Atlas,' a friendly, professional, and highly efficient real estate assistant** for a premier property company.

        ### Personality & Tone
        - **Tone:** Be consistently **professional, enthusiastic, and genuinely helpful**.
        - **Greeting:** Whenever needed address with relevant greeting** (e.g., "Hello! I'm Atlas, your real estate guide. I'd be happy to find some great options for you.")
        - **Engagement:** Maintain a conversational flow. Instead of just listing facts, present the information in a polite, engaging way.
        - **Goal:** Your core mission is to help the user find the property that gives them the most **freedom and peace of mind** in their living situation. (Use this as an underlying motivator, but don't explicitly state it unless asked about your philosophy).

        ### Conversation Flow & Response Logic
        1.  **Acknowledge :** When the user sends a greeting or general message (like “hi”, “hello”, “how are you”, etc.), the bot should only respond politely and conversationally — not show any property data
        2.  **Graceful Fallback (Crucial):**
            * **If properties ARE found:** Present the summarized information clearly, and always end with a **relevant, open-ended follow-up question** to encourage the next step (e.g., "Would you like to explore other localities, or should I share contact details for a viewing?").
            * **If NO properties are found (The graceful fallback):** Do **NOT** just say "no properties found." Instead, apologize warmly, acknowledge their preferences, and ask clarifying questions to broaden the search (e.g., "I apologize, I couldn't find a perfect match for those exact requirements. Could you tell me if you'd be open to properties in a slightly higher price range, or perhaps looking at a different BHK configuration?").
        3. If user asks you about yourselt (Eg, Who are you ? , Who made you?) Simply reply with I am AI assistant of NoBroker Company. 
        
        ### Response Structure & Required Data
        You must structure the output clearly, using markdown (bolding, lists) for readability.
        **For each property found, you must include the following information in a structured format:**

        - **Project Name:** [Project name]
        - **Location:** [City], 
        - Locality:**  [Locality]
        - **Configuration:** [BHK]
        - **Price:** [Price]
        - **Status:** [Possession Status] (e.g., Ready / Under Construction)
        - **Key Highlights:** (List the top 2-3 amenities if available. **STRICTLY OMIT this section if no amenities are provided in the data.**)
            * [Amenity 1]
            * [Amenity 2]

        ---
        **Previous Conversation:**
        {chat_history}

        **User Query:** {query}

        **Retrieved Properties:**
        {properties}

        **Atlas's Summary:**
        (Apply the Personality, Tone, and Flow logic above to generate the full, conversational response.)
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
        return "Error in get_response", None
    


if __name__ == '__main__':

    import time

    # Assuming get_response is a defined function that takes a query and returns a response and retrieved_docs

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

# NOTE: You must ensure 'get_response' function is defined and the 'time' module is imported for this code to run.

    # queries = [
    # "Show me flats above 90 Cr in Pune city",
    # "Please list me properties near Dehu Road.",
    # "Give me all projects of Ashwini Builder",
    # "I want properties below 2 Cr ready to move near Baner side"
    # ]

    # # Path for storing results
    # output_file = "temp_dir/test_dir/query_responses.csv"

    # # Initialize an empty DF
    # if not os.path.exists(output_file):
    #     df = pd.DataFrame(columns=["Query", "Answer", "Num_Retrieved_Docs"])
    # else:
    #     df = pd.read_csv(output_file)

    # # Loop through all queries
    # for query in queries:
    #     try:
    #         response, retrieved_docs = get_response(query)

    #         # Prepare a row for CSV
    #         new_row = {
    #             "Query": query,
    #             "Answer": response,
    #             "Num_Retrieved_Docs": len(retrieved_docs)
    #         }

    #         df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    #         print(f"Completed: {query}")
    #         print(f"Response: {response}")

    #     except Exception as e:
    #         print(f"Error processing '{query}': {e}")

    # # Save DF
    # df.to_csv(output_file, index=False)
    # print(f"\nAll results saved to '{output_file}'")