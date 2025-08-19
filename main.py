import streamlit as st
from response import mains_stream_lcel

st.set_page_config(initial_sidebar_state='collapsed', layout='wide')
st.title('**📖Dive**')
subheading = st.subheader('Enter an API key in the sidebar to chat with your document.', divider=True)

# Sidebar
with st.sidebar:
    st.write('**How to use**')
    st.write('1. Enter your OpenAI API key below')
    st.write('2. Upload a PDF')
    st.write('3. Ask a question about the document 💬')

    OpenAPIAI = st.text_input(
        'OpenAI API Key 🔑',
        placeholder='Paste your key 🔑 here',
        type='password'
    )


def pdfuploader(OpenAi_Api_Key, model):
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = set()

    pdfs = st.file_uploader('Upload PDF(s)', accept_multiple_files=True, type=['pdf'])
    if pdfs:
        for pdf in pdfs:
            if pdf.name not in st.session_state.uploaded_files:
                st.session_state.uploaded_files.add(pdf.name)
                st.success(f'File {pdf.name} has been processed.')
            else:
                st.warning(f'File {pdf.name} has already been uploaded.')
                break

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # New query
        if prompt := st.chat_input("Ask a question about the document?"):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                container = st.empty()
                with st.spinner("Thinking..."):
                    full_response = mains_stream_lcel(pdfs, prompt, OpenAi_Api_Key, model, container)

            st.session_state.messages.append({"role": "assistant", "content": full_response})


if OpenAPIAI:
    subheading.empty()
    model = st.selectbox('Select Model', ['gpt-4o-mini', 'gpt-5-mini', 'gpt-5-nano'])
    if not model:
        st.warning(body='Select the model to chat', icon='⚠️')
    pdfuploader(OpenAPIAI, model)
