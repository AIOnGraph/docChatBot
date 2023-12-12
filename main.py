import streamlit as st
from response import mains
import time


st.markdown("""
<style>
     [data-testid=stSidebarContent]{
        background-color: black;
            color: white;
    }
            
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
     [data-testid=stApp]{
        background-color: grey;
            color: White;
    }
            
</style>
""", unsafe_allow_html=True)
st.title('📖Dive')


with st.sidebar:
    st.write('**How to use**')
    st.write('1. Enter your OpenAI API key below')
    st.write('2. Upload a pdf')
    st.write('3. Ask a question about the document💬')

    OpenAPIAI = st.text_input('OpenAI API Key 🔑',placeholder='Paste your key(🔑) here')
    if not OpenAPIAI:
        st.warning(body='Kindly enter you API 🔑 in the side bar to chat with us',icon='⚠️')

    


# with st.expander('Select Model'):
model=st.selectbox('Select Model',['gpt-3.5-turbo','gpt-4'])
if not model:
    st.warning(body='Select the model to chat',icon='⚠️')
    

def pdfuploader(OpenAi_Api_Key, model):
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = set()
    pdfs = st.file_uploader('Upload a pdf file', accept_multiple_files=True, type=['pdf'])
    if pdfs:
        for pdf in pdfs:
            with st.spinner(text="Uploading..."):
                if pdf.name not in st.session_state.uploaded_files:
                    st.session_state.uploaded_files.add(pdf.name)   
                    st.success(f'File {pdf.name} has been processed.')
                else:
                    st.warning(f'File {pdf.name} has already been uploaded.')
                    break

        # Display chat messages from history on app rerun
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask Query?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)            
            with st.spinner(text="Thinking..."):
                response = mains(pdfs=pdfs, query=prompt, OpenAi_Api_Key=OpenAi_Api_Key, model=model)                
                print(response)
            # Display assistant response in chat message container
            with st.chat_message(name="assistant"):
                message_placeholder = st.empty()
                full_response = ""
                print(type(response), 1111111111, response)
                for chunk in response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            st.session_state.messages.append({"role": "assistant", "content": full_response})      
if OpenAPIAI:
    if model:
        pdfuploader(OpenAPIAI,model)