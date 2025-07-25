.PHONY: dev backend frontend

run-dev:
	make -j2 run-backend-dev run-frontend-dev

install:
    make -j2 run-backend-dev run-frontend-dev

install-backend:
	cd backend && uv sync

run-backend-dev:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

install-frontend:
	cd frontend && npm install

run-frontend-dev:
	cd frontend && npm run dev