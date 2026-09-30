.PHONY: up down test seed
up:
	docker compose up --build
down:
	docker compose down
test:
	cd backend && pytest -q
seed:
	docker compose exec api python -m app.seed
