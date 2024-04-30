# from flask import Flask, render_template, request, jsonify
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from flask_socketio import SocketIO, send,emit
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import os

# app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.config['SECRET'] = "secret!123"
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app,resources={r'/*':{"origins":"*"}})
load_dotenv()

os.environ["OPENAI_API_KEY"] = "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"

# Define Langchain functions
def get_vectorstore_from_url(url):
    loader = WebBaseLoader(url)
    document = loader.load()
    document_chunks = []

    for url in url:
        loader = WebBaseLoader(url)
        document = loader.load()            
        text_splitter = RecursiveCharacterTextSplitter()
        chunks = text_splitter.split_documents(document)
        document_chunks.extend(chunks)       
    vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings())

    return vector_store

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI()   
    retriever = vector_store.as_retriever()    
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)  

    return retriever_chain
    
def get_conversational_rag_chain(retriever_chain):    
    llm = ChatOpenAI()    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the below context:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])   
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)    

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input):
    retriever_chain = get_context_retriever_chain(app.config['VECTOR_STORE'])
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)    
    response = conversation_rag_chain.invoke({
        "chat_history": app.config['CHAT_HISTORY'],
        "input": user_input
    })    
    return response['answer']


def initfun():
    if 'CHAT_HISTORY' not in app.config:
        app.config['CHAT_HISTORY'] = [AIMessage(content="")]

    if 'VECTOR_STORE' not in app.config:
        url = [
            "https://www.aroopaapps.com/",  
        ]
        app.config['VECTOR_STORE'] = get_vectorstore_from_url(url)

initfun() 



@app.route('/test',methods=['GET'])
def custom_response():
    return Response("server is running successfully", status=200, mimetype='text/plain')

@app.route('/message', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.json.get('user_input')
        response = get_response(user_input)
        app.config['CHAT_HISTORY'].append(HumanMessage(content=user_input))
        app.config['CHAT_HISTORY'].append(AIMessage(content=response))
        response_data = response
        return jsonify(response_data),200



if __name__ == '__main__':
    socketio.run(app,debug=True)

        #   "https://www.aroopaapps.com/aroopa-forms/",
        #     "https://www.aroopaapps.com/aroopa-oms/",
        #     "https://www.aroopaapps.com/aroopa-campaign-manager/",
        #     "https://www.aroopaapps.com/aroopa-workflows/",
        #     "https://www.aroopaapps.com/aroopa-invoices/",
        #     "https://www.aroopaapps.com/aroopa-contact-center-management/",
        #     "https://www.aroopaapps.com/aroopa-project-management/",
        #     "https://www.aroopaapps.com/aroopa-crm/",
        #     "https://www.aroopaapps.com/aroopa-ticket-management/"