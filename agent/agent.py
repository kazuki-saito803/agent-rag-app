import os

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool


load_dotenv()
model = os.getenv("MODEL")

# def get_weather(city: str) -> dict:
#     """
#     指定された都市の天気を取得する関数
    
#     引数: 
#         city(str):都市名(英語小文字表記のみ)
        
#     戻り値:
#         dict:
#             - status(str): "success"または"error"
#             - report(str): 天気情報のメッセージ(成功時)
#             - error_message(str): エラー発生時の詳細なメッセージ
#     """
#     return {
#         "status":"success",
#         "report":f"{city}の天気は晴れです。"
#     }

# weather_agent = LlmAgent(
#     name = "weather_agent",
#     model = model,
#     description = (
#         "あなたは、ユーザーから都市の情報を受け取り、その都市の天気を案内するアシスタントです。"
#         "都市名だけの入力はその都市の天気を聞いていると判断してください。"
#         "入力された都市名を英語小文字表記に変換して、get_weatherツールに渡して。"
#         "Google検索ツールを使用して、天気情報を取得してください。"
#         "天気に関する質問以外の質問が来た場合は、conditinator_agentに任せてください。"
#     ),
#     tools = [get_weather]
# )

# google_search_agent = LlmAgent(
#     name = "google_search_agent",
#     model = model,
#     description = (
#         "あなたは、Google検索エージェントです。"
#         "ユーザーから検索キーワードを受け取り、検索結果を返してください。"
#     ),
#     tools = [google_search]
# )

# retrieve_agent = LlmAgent(
#     name = "retrieve_agent",
#     model = model,
#     description = (
#         "あなたは親しみやすい挨拶エージェントです。"
#         "ユーザーから「こんにちは」「おはよう」などの挨拶を受け取ったら、"
#         "自然な日本語で挨拶をしつつ、「都市の天気に関して質問ができます」と案内してください。"
#         "挨拶以外の質問が来た場合は、conditinator_agentに任せてください。"
#     )
# )

# conditinator_agent = LlmAgent(
#     name = "conditinator_agent",
#     model = model,
#     description = "検索と生成のエージェントを連携し、その他の質問はWeb検索してからで対応します。",
#     tools = [AgentTool(google_search_agent)],  # ビルドインツール機能を使用するエージェントの場合はAgentToolとしてtoolsに定義
#     sub_agents = [retrieve_agent, weather_agent]  # サブエージェントの定義
# )
# conditinator_agent = LlmAgent(
#     name = "conditinator_agent",
#     model = model,
#     description = "検索と生成のエージェントを連携し、その他の質問はWeb検索してからで対応します。",
#     tools = [AgentTool(google_search_agent)],  # ビルドインツール機能を使用するエージェントの場合はAgentToolとしてtoolsに定義
#     sub_agents = [retrieve_agent, weather_agent]  # サブエージェントの定義
# )

# root_agent = conditinator_agent
