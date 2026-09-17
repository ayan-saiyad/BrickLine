# Brickline

Brickline is a small LEGO release and retirement tracker. It shows upcoming dates in calendar and timeline views, keeps source links attached to each date, and makes estimates obvious instead of presenting them as confirmed.

The app has a React frontend, a FastAPI API, PostgreSQL, and a repeatable CSV importer. Docker Compose is the normal way to run it. The `deploy/` directory contains an optional Kubernetes lab for rollout and recovery practice.

## Run it

Copy the example environment file and start the stack:

```sh
cp .env.example .env
docker compose up --build
```

Open <http://localhost:3000>. The API is available at <http://localhost:8000/api/health>.

Load the included sample data:

```sh
docker compose run --rm api python -m app.cli import-data /app/data/lego-releases.csv
```

## Development

The backend and frontend can also run separately:

```sh
cd api
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
alembic upgrade head
uvicorn app.main:app --reload
```

```sh
cd web
npm install
npm run dev
```

See [docs/data-import.md](docs/data-import.md) for the import format, [docs/kubernetes.md](docs/kubernetes.md) for the optional local cluster, and [docs/lab-results.md](docs/lab-results.md) for the latest recovery exercise.
