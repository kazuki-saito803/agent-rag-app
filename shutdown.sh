# コンテナ名一覧
CONTAINERS=("agent-ui" "elastic-search" "indexing-server" "mcp-server" "indexing-ui")

# イメージ名一覧（docker images で確認した正確な名前）
IMAGES=("googleadk-sample-agent-ui:latest" "googleadk-sample-elasticsearch:latest" "googleadk-sample-indexing-server:latest" "googleadk-sample-mcp-server:latest" "googleadk-sample-indexing-ui:latest")

echo "=== コンテナ停止・削除 ==="
for c in "${CONTAINERS[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -w "$c" > /dev/null; then
        docker stop "$c"
        docker rm "$c"
        echo "Stopped and removed container: $c"
    else
        echo "Container not found: $c"
    fi
done

echo "=== イメージ削除 ==="
for i in "${IMAGES[@]}"; do
    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -w "$i" > /dev/null; then
        docker rmi -f "$i"
        echo "Removed image: $i"
    else
        echo "Image not found: $i"
    fi
done

echo "=== 完了 ==="