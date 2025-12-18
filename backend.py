import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from typing import List

# =========================
# ENV & DATA DIR
# =========================
load_dotenv()
DATA_DIR = "data"

# =========================
# LANGCHAIN (LATEST)
# =========================
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader

# ==============================
# LOAD DOCUMENTS
# ==============================
def load_documents() -> List[Document]:
    documents = []

    if not os.path.exists(DATA_DIR):
        return documents

    for file in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, file)

        try:
            if file.endswith(".csv"):
                loader = CSVLoader(path)
                documents.extend(loader.load())

            elif file.endswith(".pdf"):
                loader = PyPDFLoader(path)
                documents.extend(loader.load())

            elif file.endswith(".txt"):
                loader = TextLoader(path)
                documents.extend(loader.load())
        except Exception as e:
            print(f"Skipping {file}: {e}")

    return documents

# ==============================
# TEXT SPLITTING
# ==============================
def split_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)

# ==============================
# EMBEDDINGS
# ==============================
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# ==============================
# VECTOR STORE
# ==============================
def build_vectorstore():
    docs = load_documents()
    if not docs:
        return None

    chunks = split_documents(docs)
    embeddings = get_embeddings()
    return FAISS.from_documents(chunks, embeddings)

VECTORSTORE = build_vectorstore()

# ==============================
# GROQ LLM
# ==============================
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY")
)

# ==============================
# BULLET-STYLE PROMPT
# ==============================
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a professional healthcare assistant.

Answer the question ONLY using the context below.
Format the answer as clear step-by-step bullet points.
Each point must be short and user friendly.
Do NOT include model info, metadata, or explanations.

Context:
{context}

Question:
{question}

Answer (bullet points only):
"""
)

# ==============================
# RAG PIPELINE
# ==============================
def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

if VECTORSTORE:
    retriever = VECTORSTORE.as_retriever(search_kwargs={"k": 4})

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )
else:
    rag_chain = None

def rag_query_pipeline(question: str) -> str:
    if not rag_chain:
        return "⚠️ Knowledge base is empty."

    response = rag_chain.invoke(question)

    # Extract clean text only
    if hasattr(response, "content"):
        return response.content.strip()

    return str(response).strip()

# ==============================
# APPOINTMENT FUNCTIONS
# ==============================
def list_doctors():
    try:
        return pd.read_csv(f"{DATA_DIR}/Doctors.csv")
    except:
        return None

def save_appointment(data):
    try:
        file = f"{DATA_DIR}/Appointments.csv"
        df = pd.read_csv(file) if os.path.exists(file) else pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(file, index=False)
        return True
    except:
        return False

# ==============================
# MEDICINES FUNCTIONS
# ==============================
def list_medicines():
    try:
        return pd.read_csv(f"{DATA_DIR}/Medicine.csv")
    except:
        return None

def place_order(phone, address, medicine, qty, payment):
    try:
        meds = pd.read_csv(f"{DATA_DIR}/Medicine.csv")
        orders_file = f"{DATA_DIR}/orders.csv"

        med_row = meds[meds["Medicine_Name"] == medicine].iloc[0]
        total = int(med_row["Price"]) * qty + 50

        order = {
            "Phone": phone,
            "Address": address,
            "Medicine": medicine,
            "Quantity": qty,
            "Payment": payment,
            "Total_Amount": total,
            "Status": "Confirmed",
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if os.path.exists(orders_file):
            df = pd.read_csv(orders_file)
            df = pd.concat([df, pd.DataFrame([order])], ignore_index=True)
        else:
            df = pd.DataFrame([order])

        df.to_csv(orders_file, index=False)
        return True
    except Exception as e:
        print(e)
        return False

def list_orders():
    try:
        return pd.read_csv(f"{DATA_DIR}/orders.csv")
    except:
        return None

# ==============================
# DIAGNOSIS FUNCTIONS
# ==============================
def save_diagnosis(data):
    try:
        file = f"{DATA_DIR}/Diagnosis.csv"
        df = pd.read_csv(file) if os.path.exists(file) else pd.DataFrame()
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(file, index=False)
        return True
    except:
        return False

def list_diagnosis():
    try:
        return pd.read_csv(f"{DATA_DIR}/Diagnosis.csv")
    except:
        return None