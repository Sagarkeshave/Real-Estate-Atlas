---
title: Real Estate Atlas RAG Assistant
emoji: 🏠
colorFrom: purple
colorTo: indigo
# The sdk must be set to docker to confirm the configuration
sdk: docker
# Add an app port variable to confirm the running port
app_port: 5051
---


# Real Estate Atlas RAG Chatbot 🏡

Flask application for real-estate insights and conversational assistance, powered by LangChain, Gemini, and Chroma DB for retrieval-augmented generation.


🎥 **Demo Video:** [Watch on Loom](https://www.loom.com/share/309a8edf39324713ae1080e744f868ed)


---

## About

Real Estate Atlas is a conversational assistant (chatbot) tailored for real estate domain queries. It uses **Retrieval-Augmented Generation (RAG)** to fetch domain-specific data (via Chroma DB) and combine with generative models (LangChain + Gemini) to deliver informed responses.

## Features

- Conversational Q&A for real estate topics  
- Retrieval of domain data (e.g. property features, market trends)  
- Integration with generative model (Gemini) to produce fluent, context-aware replies  
- Dockerized deployment for easy setup  
- Modular architecture for ingestion, preprocessing, and model orchestration  


### Setup & Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Sagarkeshave/Real-Estate-Atlas.git
   cd Real-Estate-Atlas
   ```
2. Create a virtual environment
    
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Ensure configuration / secrets are set
    #  In .env 
    ```bash
    GOOGLE_API_KEY = "YOUR_API_KEY"
    ```

### Usage

Once running, you can send queries via the frontend interface or via HTTP API endpoints (e.g. /chat or similar). The system will:

1. Ingest the user prompt

2. Use Chroma DB to find relevant document/context

3. Combine context + prompt and send to Gemini model

4. Return generated answer to user

### Project Structure
```bash
├── app.py
├── st_app.py
├── dataIngestion.py
├── dataPreprocessing.py
├── rag.py
├── requirements.txt
├── Dockerfile
├── templates/
├── static/
└── vectore_DB/ chroma_langchain_DB/
```

