from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

index_name = "documents"

# インデックス作成（既存なら削除して再作成）
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)

index_body = {
    "mappings": {
        "properties": {
            "content": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 768,  # 埋め込み次元数 (例: sentence-transformers)
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

es.indices.create(index=index_name, body=index_body)
print("Index created:", index_name)