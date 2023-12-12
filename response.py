import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import  RecursiveCharacterTextSplitter
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from openai import AuthenticationError
import sys


sys.modules['sqlite3'] = __import__('pysqlite3')

def pdfText(pdfs):
    text = ''
    for pdf in pdfs:
        pdf_reader = PdfReader(pdf)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def splitText(text_from_pdf):
    textSpliter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100)
    Split_Text = textSpliter.split_text(text_from_pdf)
    return Split_Text

def vectorDataBaseEmbedding(splitedText, query):
    embed = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    VectorDataBase = Chroma.from_texts(splitedText, embed)
    docs = VectorDataBase.similarity_search(query, k=5)
    return docs

def chain(vector, query, OpenAi_Api_Key, model):
    try:
        chat = ChatOpenAI(api_key=OpenAi_Api_Key, temperature=0.0, model=model)
        chain = load_qa_chain(llm=chat, chain_type='stuff', verbose=True)
        response = chain.run({'input_documents': vector, 'question': query})
        return response
    except AuthenticationError:
        st.warning(
            body='AuthenticationError : Please provide correct api key 🔑' ,icon='🤖')
        return ""

def mains(pdfs, query, OpenAi_Api_Key, model):
    text_from_pdf = pdfText(pdfs)
    splitedText = splitText(text_from_pdf)
    vector = vectorDataBaseEmbedding(splitedText, query)
    getresponse = chain(vector, query, OpenAi_Api_Key, model)
    return getresponse
