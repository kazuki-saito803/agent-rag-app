from fastapi import FastAPI, HTTPException, Query,  UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from docx import Document as DocxDocument
import math

load_dotenv()
ELASTICSEARCH_ENDPOINT = os.getenv("ELASTICSEARCH_ENDPOINT")

# --- ElasticSearch 接続 ---
es = Elasticsearch(ELASTICSEARCH_ENDPOINT)

# --- Hugging Face 埋め込みモデル ---
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
VECTOR_DIM = embedding_model.get_sentence_embedding_dimension()

# --- FastAPI 初期化 ---
app = FastAPI(title="RAG Document Indexing API")

# --- Pydantic モデル ---
class IndexRequest(BaseModel):
    index_name: str

class Document(BaseModel):
    title: str
    content: str

class ChunkedDocument(BaseModel):
    index_name: str
    title: str
    content: str
    chunk_size: Optional[int] = 200  # 1チャンクの文字数デフォルト200

# --- ファイル前処理関数 ---
def preprocess_text(text: str, chunk_size: int = 500) -> List[dict]:
    text = text.replace("\r\n", "\n").strip()
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    indexed_docs = []
    for i, chunk in enumerate(chunks):
        vector = embedding_model.encode(chunk).tolist()
        indexed_docs.append({"content": chunk, "embedding": vector, "chunk_number": i+1})
    return indexed_docs

def preprocess_file(file_path: str, chunk_size: int = 500) -> List[dict]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif ext == ".docx":
        doc = DocxDocument(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("対応していないファイル形式です。txtかdocxを使用してください。")
    return preprocess_text(text, chunk_size)

# --- インデックス作成 ---
@app.post("/create_index/")
def create_index(request: IndexRequest):
    index_body = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "embedding": {"type": "dense_vector", "dims": VECTOR_DIM}
            }
        }
    }
    try:
        es.indices.create(index=request.index_name, body=index_body, ignore=400)
        return {"message": f"Index '{request.index_name}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ドキュメント登録（チャンク化対応） ---
@app.post("/index_document_chunked/")
def index_document_chunked(doc: ChunkedDocument):
    try:
        chunks = preprocess_text(doc.content, doc.chunk_size)
        for i, chunk_info in enumerate(chunks):
            doc_body = {
                "title": f"{doc.title} - chunk {i+1}",
                "content": chunk_info["content"],
                "embedding": chunk_info["embedding"]
            }
            es.index(index=doc.index_name, document=doc_body)
        return {"message": f"{len(chunks)} chunks from document '{doc.title}' indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ファイルアップロードからインデックスに登録するエンドポイント ---
@app.post("/index_file/")
async def index_file(file: UploadFile = File(...), index_name: str = "rag_docs", chunk_size: int = 500):
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    try:
        chunks = preprocess_file(tmp_path, chunk_size)
        for i, chunk_info in enumerate(chunks):
            doc_body = {
                "title": f"{file.filename} - chunk {i+1}",
                "content": chunk_info["content"],
                "embedding": chunk_info["embedding"]
            }
            es.index(index=index_name, document=doc_body)
        return {"message": f"{len(chunks)} chunks from file '{file.filename}' indexed successfully."}
    finally:
        os.remove(tmp_path)

# --- ハイブリッド検索エンドポイント ---
@app.get("/search/")
def search(index_name: str, query: str, top_k: int = 3):
    try:
        query_vector = embedding_model.encode(query).tolist()
        hybrid_query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["title", "content"]
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }

        res = es.search(index=index_name, body=hybrid_query)
        results = [
            {"title": hit["_source"]["title"], "score": hit["_score"]}
            for hit in res["hits"]["hits"]
        ]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_indices/")
def list_indices():
    try:
        indices = es.cat.indices(format="json")
        index_names = [idx["index"] for idx in indices]
        return {"indices": index_names}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/index_content/")
def index_content(index_name: str = Query(..., description="取得したいIndex名")):
    try:
        # 全件取得（sizeは適宜調整）
        res = es.search(index=index_name, query={"match_all": {}}, size=100)
        documents = [
            {
                "title": hit["_source"].get("title"),
                "content": hit["_source"].get("content"),
                "score": hit["_score"]
            }
            for hit in res["hits"]["hits"]
        ]
        return {"index": index_name, "documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))