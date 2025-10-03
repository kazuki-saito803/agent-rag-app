import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from fastmcp import FastMCP

load_dotenv()
mcp_server_port = int(os.getenv("MCP_SEVER_PORT"))
ELASTICSEARCH_ENDPOINT = os.getenv("ELASTICSEARCH_ENDPOINT")
mcp = FastMCP("MyRAGMCP")

# --- ElasticSearch 接続 ---
es = Elasticsearch(ELASTICSEARCH_ENDPOINT)

# --- Hugging Face 埋め込みモデル ---
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
VECTOR_DIM = embedding_model.get_sentence_embedding_dimension()

# --- ハイブリッド検索エンドポイント ---
@mcp.tool()
def search(index_name: str, query: str, top_k: int = 3):
    """
    指定されたインデックスからハイブリッド検索を行います。

    このツールは以下を組み合わせた検索を提供します:
    - テキスト検索（description, content フィールドに対する multi_match）
    - ベクトル検索（sentence-transformers による埋め込みベクトル）

    Args:
        index_name (str): 検索対象のインデックス名
        query (str): 検索クエリ
        top_k (int): 取得件数（デフォルト3）

    Returns:
        dict: 検索結果。
              各要素には description, content, score が含まれます。
    """
    try:
        query_vector = embedding_model.encode(query).tolist()
        knn_query = {
            "knn": {
                "field": "embedding",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": 100
            }
        }

        res = es.search(index=index_name, body=knn_query)
        results = [
            {
                "description": hit["_source"].get("description", ""),
                "content": hit["_source"].get("content", ""),
                "score": hit["_score"]
            }
            for hit in res["hits"]["hits"]
        ]
        return {"results": results}
    except Exception as e:
        raise RuntimeError(f"検索処理でエラーが発生しました: {str(e)}")

# --- インデックス一覧 ---
@mcp.tool()
def list_indices():
    """
    利用可能なインデックスの一覧を取得します。

    Args:
        なし

    Returns:
        dict: インデックスの辞書。
              各要素には index (インデックス名) と description (説明) が含まれます。
              descriptionはIndexの説明のためユーザーからの入力に応じてどのIndexでの検索が適切かを判断することができます。
              description は _meta_ ドキュメントから取得できない場合は空文字となります。
    """
    try:
        # 全インデックス名取得
        indices_info = es.indices.get(index="*")
        indices_list = []

        for index_name in indices_info.keys():
            # 各インデックスの _meta_ ドキュメント取得
            try:
                meta_res = es.get(index=index_name, id="_meta_")
                description = meta_res["_source"].get("description", "")
            except:
                description = ""  # _meta_ がない場合は空文字

            indices_list.append({"index": index_name, "description": description})

        return {"indices": indices_list}

    except Exception as e:
        raise RuntimeError(f"検索エラー: {str(e)}")


if __name__ == "__main__":
    mcp.run(transport="http", port=mcp_server_port)