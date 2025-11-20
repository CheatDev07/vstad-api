# Stop all containers
docker-compose down

# Rebuild the images
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Check logs
docker logs -f vstad-api