.ONESHELL:
.DEFAULT_GOAL := run

VIRTUALENV = venv
PYTHON = $(VIRTUALENV)/bin/python3
PIP = $(VIRTUALENV)/bin/pip
VERSION=0.0.3

clean:
	@rm -rf $(VIRTUALENV)
	@rm -rf __pycache__

venv: clean
	@python3 -m venv $(VIRTUALENV)
	@chmod +x $(VIRTUALENV)/bin/activate
	@. $(VIRTUALENV)/bin/activate
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install --no-cache-dir -r config/requirements.txt

setup: venv
	@. $(VIRTUALENV)/bin/activate

dependencies:
	@python3 -m pip install --upgrade pip
	@pip3 install --no-cache-dir -r config/requirements.txt

run:
	$(PYTHON) main.py

lunch:
	python3 main.py

build:
	docker build --build-arg env_arg=pdn -t bongga/parrot-assistant-api:$(VERSION) -f config/Dockerfile .

docker:
	docker run -itd --name parrot-assistant-api-container --replicas 2 -p 8000:8000 --restart unless-stopped bongga/parrot-assistant-api:$(VERSION)

deploy:
	docker push bongga/parrot-assistant-api:$(VERSION)
 
delete:
	docker rmi -f bongga/parrot-assistant-api:$(VERSION)
	docker container prune -f
	docker image prune -f

.PHONY: venv activate clean build docker delete deploy