# app.py

import streamlit as st
import json
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage

# 從 alias_utils 匯入我們的標準化函式
from alias_utils import normalize_query

# ------------------------------------------------------------------
# 1. 將所有耗時的前置作業打包成一個函式，並用 cache_resource 快取
# ------------------------------------------------------------------
@st.cache_resource
def load_rag_pipeline():
    """
    這個函式會執行所有耗時的初始化操作，並且 Streamlit 會將結果快取起來。
    """
    print("--- 執行耗時的前置作業 ---")
    
    # --- 設定您的 Ollama 伺服器位址 ---
    # --- 請將 IP 位址換成您伺服器電腦的區域網路 IP ---
    OLLAMA_SERVER_URL = "http://192.168.50.56:11434" 


    # 1.1 載入並處理知識庫 (從 chunks_raw.json)
    embeddings = OllamaEmbeddings(base_url=OLLAMA_SERVER_URL, model="nomic-embed-text")
    
    try:
        with open("./chunks_raw.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("找不到 'chunks_raw.json'。請確保檔案與 app.py 在同一個資料夾中。")

    # 將 JSON 資料轉換為 LangChain 的 Document 格式
    docs = []
    for item in data:
        # 將 'text' 作為主要內容，其他資訊作為 metadata
        doc = Document(page_content=item.get('text', ''), metadata={
            'url': item.get('url', ''),
            'title': item.get('title', ''),
            'category': item.get('category', '')
        })
        docs.append(doc)

    if not docs:
        raise ValueError("從 'chunks_raw.json' 載入的知識庫文件為空！")

    # 1.2 建立向量資料庫 (直接使用載入的 docs)
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    retriever = vectorstore.as_retriever()

    # 1.3 定義各種處理鏈 (Chains)
    # -- 查詢重寫鏈 --
    contextualize_q_system_prompt = """Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages([("system", contextualize_q_system_prompt), ("human", "{chat_history}\n\nFollow Up Input: {question}")])
    contextualize_q_chain = contextualize_q_prompt | Ollama(base_url=OLLAMA_SERVER_URL,model="llama3:8b", temperature=0.1) | StrOutputParser()
    
    # -- 問答鏈 (更新後的 Prompt) --
    qa_system_prompt = """你是一個專業的醫美諮詢助理，你的名字是「Rainssom AI」。請根據我提供的「參考資料」來回答使用者的問題。如果參考資料中沒有答案，就說你不知道。請使用台灣人習慣的繁體中文來回答，並盡量保持答案簡潔。
    ---
    參考資料:
    {context}
    ---
    """
    qa_prompt = ChatPromptTemplate.from_messages([("system", qa_system_prompt), ("human", "{question}")])
    qa_chain = qa_prompt | Ollama(base_url=OLLAMA_SERVER_URL,model="llama3:8b", temperature=0.1) | StrOutputParser()

    print("--- 前置作業完成 ---")
    
    return retriever, contextualize_q_chain, qa_chain

# ------------------------------------------------------------------
# 2. Streamlit 應用程式主體
# ------------------------------------------------------------------

# 設定頁面標題
st.title("🚀 Rainssom 醫美智能助理")

# 呼叫快取函式來載入 RAG pipeline
try:
    retriever, contextualize_q_chain, qa_chain = load_rag_pipeline()
except Exception as e:
    st.error(f"初始化 RAG 流程失敗: {e}")
    st.stop()


# 初始化 session_state 中的對話歷史
if "messages" not in st.session_state:
    st.session_state.messages = [AIMessage(content="您好！我是 Rainssom AI，請問有什麼可以為您服務的嗎？")]

# 顯示歷史對話訊息
for message in st.session_state.messages:
    with st.chat_message(message.type):
        st.markdown(message.content)

# 接收使用者輸入
if prompt := st.chat_input("請在這裡輸入您的問題..."):
    # 將使用者訊息存入 session_state 並顯示在畫面上
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("human"):
        st.markdown(prompt)

    # 準備顯示 AI 回應
    with st.chat_message("ai"):
        # 使用 spinner 讓使用者知道 AI 正在思考
        with st.spinner("思考中..."):
            # 1. 查詢重寫 (處理對話歷史)
            rewritten_question = contextualize_q_chain.invoke({
                "chat_history": [msg.content for msg in st.session_state.messages[:-1]],
                "question": prompt
            })

            # 2. **新增**：標準化查詢中的關鍵字
            normalized_question = normalize_query(rewritten_question)

            # 3. 檢索 (使用標準化後的問題)
            retrieved_docs = retriever.invoke(normalized_question)
            context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])

            # 4. 生成答案
            answer = qa_chain.invoke({
                "context": context_text,
                "question": rewritten_question # 使用重寫後、但未標準化的問題，讓LLM看到最原始的意圖
            })
            
            # 在畫面上顯示 AI 回應
            st.markdown(answer)

    # 將 AI 回應也存入 session_state
    st.session_state.messages.append(AIMessage(content=answer))