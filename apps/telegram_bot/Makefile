.ONESHELL:
.DEFAULT_GOAL := run

#VIRTUALENV := $(shell bash -c 'read -p "Set the virtualenv name: " environment; echo $$environment')
VIRTUALENV = venv
PYTHON = $(VIRTUALENV)/bin/python3
PIP = $(VIRTUALENV)/bin/pip

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

run:
	@$(PYTHON) main.py

build:
	docker build -t bongga/parrot-telegram-bot:0.0.1 -f config/Dockerfile .

build-onrender:
	docker build --platform=linux/amd64 -t bongga/parrot-telegram-bot:0.0.1 -f config/Dockerfile.onrender .

docker:
	docker run -itd --name parrot-telegram-bot-container bongga/parrot-telegram-bot:0.0.1

deploy:
	docker push bongga/parrot-telegram-bot:0.0.1
 
delete:
	docker rmi -f bongga/parrot-telegram-bot:0.0.1
	docker container prune -f
	docker image prune -f

.PHONY: venv activate clean
