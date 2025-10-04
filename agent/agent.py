import os

from dotenv import load_dotenv
from fastmcp import Client

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search

load_dotenv()
model = os.getenv("MODEL")
MCP_SEVER_URL = os.getenv("MCP_SEVER_URL")

async def get_tools():
    """
    MCPサーバーで提供されているツールを取得する関数
    
    引数: 
        なし
        
    戻り値:
        dict:
    """
    async with Client(f"{MCP_SEVER_URL}/mcp") as client:
        # ツール一覧を確認
        tools = await client.list_tools()
        return tools

async def call_tools(tool_name: str, args: dict)->dict:
    """
    MCPサーバーの指定されたツールを呼び出すためのツール
    
    引数: 
        tool_name(str): MCPサーバーで提供されているツール名
        args(dict): 引数名とそれに紐づく値の辞書
        例
        {
            "name": "Bob"
        }
        
    戻り値:
        dict:各Toolが返す辞書
    """
    async with Client(f"{MCP_SEVER_URL}/mcp") as client:
        # ツール一覧を確認
        result = await client.call_tool(tool_name, args)
        return result

mcp_client_agent = LlmAgent(
    name = "mcp_client_agent",
    model = model,
    description = (
        "あなたは、mcpサーバーと通信するためのツールを使い、orchestrator_agentからの指示に従ってRAGの検索を行うアシスタントです。"
        "与えられたmcpサーバーに接続するツールを元にしてRAG検索を行い、結果をorchestrator_agentに返してください。"
    ),
    tools=[call_tools]
)

google_search_agent = LlmAgent(
    name = "google_search_agent",
    model = model,
    description = (
        "あなたは、Google検索エージェントです。"
        "ユーザーから検索キーワードを受け取り、検索結果を返してください。"
    ),
    tools = [google_search]
)
get_tool_agent = LlmAgent(
    name = "get_tool_agent",
    model = model,
    description = (
        "あなたは、mcpサーバーのツール一覧とその説明を取得し、orchestrator_agentにその結果を返すアシスタントです。"
        "orchestrator_agentからリクエストをもらったら, 与えられたget_toolsのツールを実行してその結果を返してください。"
    ),
    tools = [get_tools]
)

orchestrator_agent = LlmAgent(
    name = "orchestrator_agent",
    model = model,
    description = (
        "あなたは、ユーザーからのリクエストに応じて各種sub_agentを利用して回答の材料となる情報を取得し、最終的な回答を行うアシスタントです。"
        "まず、質問が与えられたら、get_tool_agentでMCPサーバーのツールのメタ情報を取得し、どのようなツールが使えそうかを確認してください。"
        "その後に、mcp_client_agentを使ってデータベースからユーザーの質問に応じた情報を取得します。"
        "そしてその情報を元にしてあなたが最終的な回答を生成してユーザーに返してください。"
    ),
    sub_agents = [mcp_client_agent, get_tool_agent]
)

root_agent = orchestrator_agent