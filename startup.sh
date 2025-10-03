# DockerfileからDocker imageをビルド
docker build -t agent:latest -f Dockerfile.agent .
docker build -t elastic:latest -f Dockerfile.elastic .
docker build -t index:latest -f Dockerfile.index .
docker build -t mcp:latest -f Dockerfile.mcp .
docker build -t ui:latest -f Dockerfile.ui .

# ビルドしたイメージをデタッチモードで実行
docker run -d -p 8000:8000 --name agent-ui agent:latest
docker run -d -p 9200:9200 --name elastic-search elastic:latest
docker run -d -p 8002:8002 --name indexing-server index:latest
docker run -d -p 8001:8001 --name mcp-server mcp:latest
docker run -d -p 8501:8501 --name indexing-ui ui:latest