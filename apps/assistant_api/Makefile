.ONESHELL:
.DEFAULT_GOAL := run

VIRTUALENV = venv
PYTHON = $(VIRTUALENV)/bin/python3
PIP = $(VIRTUALENV)/bin/pip

clean:
	@rm -rf $(VIRTUALENV)
	@rm -rf __pycache__

venv: clean
	@$(PYTHON) -m venv $(VIRTUALENV)
	@chmod +x $(VIRTUALENV)/bin/activate
	@. $(VIRTUALENV)/bin/activate
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install --no-cache-dir -r config/requirements.txt

setup: venv
	@. $(VIRTUALENV)/bin/activate	

run:
	$(PYTHON) -m uvicorn main:AssistantApi.app --host 0.0.0.0 --port 8000 --reload --loop asyncio --env-file config/.env

build:
	docker build -t bongga/parrot-assistantant-api:0.0.1 -f config/Dockerfile .

build-onrender:
	docker build --platform=linux/amd64 -t bongga/parrot-assistantant-api:0.0.1 -f config/Dockerfile.onrender .

docker:
	docker run -itd --name parrot-assistant-api-container -p 8000:8000 bongga/parrot-assistantant-api:0.0.1

deploy:
	docker push bongga/parrot-assistantant-api:0.0.1
 
delete:
	docker rmi -f bongga/parrot-assistantant-api:0.0.1
	docker container prune -f
	docker image prune -f

.PHONY: venv activate clean