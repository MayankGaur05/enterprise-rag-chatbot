# enterprise-rag-chatbot
A chatbot application based on RAG pattern

## Run the Streamlit application

```bash

streamlit run  frontend/app.py
```
## Configuration

1. Copy .env.example to .env
2. Update values for your machine

Run backend:
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

Run frontend:
streamlit run frontend/app.py

Note:
OS-level environment variables override values in .env.
