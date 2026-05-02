# Docker Deployment Commands

## Rebuild & Restart

```bash
# Restart a single service after a code change
docker compose up -d --build web

# Pull latest code and redeploy
git pull
docker compose up -d --build
```

## Logs

```bash
# View real-time logs for one service
docker compose logs -f celery_worker

# View logs for all services
docker compose logs -f
```

## Management Commands

```bash
# Run a Django shell
docker compose exec web python manage.py shell

# Run migrations
docker compose exec web python manage.py migrate

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Create a superuser
docker compose exec web python manage.py createsuperuser
```

## Start & Stop

```bash
# Start all services in the background
docker compose up -d

# Stop everything (data is preserved)
docker compose down

# Stop and wipe all data (careful — deletes volumes!)
docker compose down -v
```

## Status & Debugging

```bash
# Check all containers are running
docker compose ps

# Test the app responds
curl -I http://18.207.46.68/

# Open a shell inside a container
docker compose exec web bash
```