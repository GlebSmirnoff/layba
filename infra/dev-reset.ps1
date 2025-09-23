docker compose -f "$PSScriptRoot/docker-compose.yml" down -v
docker volume prune -f
