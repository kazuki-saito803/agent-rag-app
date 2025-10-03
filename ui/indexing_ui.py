import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()
API_URL = os.getenv("API_SERVER_URL")

st.title("RAG Document Indexing UI")

# --- 1. インデックス作成 ---
st.subheader("1. インデックス作成")
index_name_create = st.text_input("インデックス名を入力", key="index_name_create")
index_description_create = st.text_input("説明 (description)", key="index_desc_input")
if st.button("Create Index", key="btn_create_index"):
    if index_name_create and index_description_create:
        res = requests.post(
            f"{API_URL}/create_index/",
            json={"index_name": index_name_create, "description": index_description_create}
        )
        st.write(res.json())
    else:
        st.warning("インデックス名と説明を入力してください。")

# --- 2. テキスト登録（チャンク化） ---
st.subheader("2. テキストを登録（チャンク化）")
index_name_text = st.text_input("対象インデックス名 (テキスト用)", key="index_name_text")
description_text = st.text_input("説明 (description)", key="desc_text_input")
content_text = st.text_area("内容", key="content_text")
chunk_size_text = st.number_input(
    "チャンクサイズ", min_value=50, max_value=1000, value=200, step=50, key="chunk_size_text"
)
if st.button("Index Text", key="btn_index_text"):
    if index_name_text and description_text and content_text:
        payload = {
            "index_name": index_name_text,
            "description": description_text,
            "content": content_text,
            "chunk_size": chunk_size_text
        }
        res = requests.post(f"{API_URL}/index_document_chunked/", json=payload)
        st.write(res.json())
    else:
        st.warning("すべてのフィールドを入力してください。")

# --- 3. ファイルアップロード ---
st.subheader("3. ファイルアップロード（txt, docx）")
index_name_file = st.text_input("対象インデックス名 (ファイル用)", key="index_name_file")
uploaded_file = st.file_uploader("ファイルを選択", type=["txt", "docx"], key="file_uploader")
chunk_size_file = st.number_input(
    "チャンクサイズ (ファイル)", min_value=50, max_value=1000, value=500, step=50, key="chunk_size_file"
)
if st.button("Index File", key="btn_index_file"):
    if uploaded_file and index_name_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = requests.post(
            f"{API_URL}/index_file/?index_name={index_name_file}&chunk_size={chunk_size_file}",
            files=files
        )
        st.write(res.json())
    else:
        st.warning("インデックス名とファイルを指定してください。")

# --- 4. 検索 ---
st.subheader("4. 検索")
index_name_search = st.text_input("検索対象インデックス", key="index_name_search")
query_text = st.text_input("検索クエリ", key="query_text")
top_k = st.number_input(
    "取得件数", min_value=1, max_value=20, value=3, key="top_k"
)
if st.button("Search", key="btn_search"):
    if index_name_search and query_text:
        params = {"index_name": index_name_search, "query": query_text, "top_k": top_k}
        res = requests.get(f"{API_URL}/search/", params=params)
        if res.status_code == 200:
            results = res.json().get("results", [])
            for r in results:
                st.markdown(f"**{r['content']}** (score: {r['score']:.3f})")
        else:
            st.error(res.json())
    else:
        st.warning("インデックス名と検索クエリを入力してください。")

# --- 5. インデックス一覧表示 ---
st.subheader("5. インデックス一覧")
if st.button("List Indices", key="btn_list_indices"):
    res = requests.get(f"{API_URL}/list_indices/")
    st.write(res.json())

# --- 6. インデックス内容確認 ---
st.subheader("6. インデックス内容確認")
index_name_view = st.text_input("確認したいインデックス名", key="index_name_view")
if st.button("View Index Content", key="btn_view_index_content"):
    if index_name_view:
        res = requests.get(f"{API_URL}/index_content/", params={"index_name": index_name_view})
        if res.status_code == 200:
            documents = res.json().get("documents", [])
            for doc in documents:
                st.markdown(f"**Description:** {doc['description']}")
                st.markdown(f"**Content:** {doc['content']}")
                st.markdown(f"Score: {doc['score']:.3f}")
                st.markdown("---")
        else:
            st.error(res.json())
    else:
        st.warning("インデックス名を入力してください。")

# --- 7. インデックス削除 ---
st.subheader("7. インデックス削除")
index_name_delete = st.text_input("削除したいインデックス名", key="index_name_delete")
if st.button("Delete Index", key="btn_delete_index"):
    if index_name_delete:
        res = requests.delete(
            f"{API_URL}/delete_index/",
            params={"index_name": index_name_delete}
        )
        if res.status_code == 200:
            st.success(res.json().get("message"))
        else:
            st.error(res.json().get("detail", "削除に失敗しました"))
    else:
        st.warning("削除するインデックス名を入力してください。")