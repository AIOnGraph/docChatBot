from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from openai import AuthenticationError
import streamlit as st
import sys

# --- Fix sqlite issue for Chroma on some environments ---
sys.modules['sqlite3'] = __import__('pysqlite3')


# ---- PDF to Text ----
def pdfText(pdfs):
    text = ""
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text


# ---- Split Text ----
def splitText(text_from_pdf):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_text(text_from_pdf)


# ---- Embedding + Vector DB ----
def vectorDataBaseEmbedding(splitedText, query, api_key):
    embed = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
    db = Chroma.from_texts(splitedText, embed)
    docs = db.similarity_search(query, k=5)
    return docs


# ---- Main Pipeline (LCEL) ----
def mains_stream_lcel(pdfs, query, api_key, model, container):
    try:
        # 1. Extract + split
        text = pdfText(pdfs)
        chunks = splitText(text)

        # 2. Embed + retrieve
        docs = vectorDataBaseEmbedding(chunks, query, api_key)
        context = "\n\n".join(d.page_content for d in docs)

        # 3. Build LCEL pipeline
        prompt = ChatPromptTemplate.from_template(
            "Answer the question based only on the following context:\n{context}\n\nQuestion: {question}"
        )
        llm = ChatOpenAI(api_key=api_key, model=model, temperature=0.2, streaming=True)
        chain = prompt | llm   # no parser

        # 4. Stream results
        inputs = {"context": context, "question": query}
        full_response = ""
        for chunk in chain.stream(inputs):
            print(chunk,"chunk")
            if chunk.content:   # AIMessageChunk
                full_response += chunk.content
                container.markdown(full_response + "▌")

        container.markdown(full_response)  # Final flush
        return full_response

    except AuthenticationError:
        st.warning("AuthenticationError : Please provide correct API key 🔑", icon="🤖")
        return ""
