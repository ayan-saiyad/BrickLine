.PHONY: dev down test lint import-data

dev:
	docker compose up --build

down:
	docker compose down

test:
	cd api && pytest
	cd web && npm test -- --run

lint:
	cd api && ruff check .
	cd web && npm run lint

import-data:
	docker compose run --rm api python -m app.cli import-data /app/data/lego-releases.csv

