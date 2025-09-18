.PHONY: dev test up seed fmt

VENV=.venv
PYTHON?=python3

$(VENV)/bin/activate: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(PYTHON) -c "import tomllib, pathlib; data=tomllib.loads(pathlib.Path('pyproject.toml').read_text()); pathlib.Path('requirements.lock').write_text('\n'.join(data['project']['dependencies']))"
	$(VENV)/bin/pip install -r requirements.lock

venv: $(VENV)/bin/activate

fmt: venv
	$(VENV)/bin/ruff check app/backend --fix
	$(VENV)/bin/mypy app/backend

seed: venv
	$(VENV)/bin/python app/backend/scripts/seed.py

backend-dev: venv
	cd app/backend && ../../$(VENV)/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd app/frontend && npm install && npm run dev

dev:
	make -j2 backend-dev frontend-dev

up:
	docker compose -f app/infra/docker-compose.yml up --build

test: venv
	$(VENV)/bin/pytest app/backend/tests
