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

dependencies:
	@python3 -m pip install --upgrade pip
	@pip3 install --no-cache-dir -r config/requirements.txt

run:
	@$(PYTHON) main.py

lunch:
	python3 main.py

build.dev:
	docker build --platform=linux/amd64 --build-arg env_arg=dev -t bongga/parrot-telegram-bot:0.0.1.dev -f config/Dockerfile .

build.pdn:
	docker build --platform=linux/amd64 --build-arg env_arg=pdn -t bongga/parrot-telegram-bot:0.0.1 -f config/Dockerfile .

docker:
	docker run -itd --name parrot-telegram-bot-container bongga/parrot-telegram-bot:0.0.1

deploy:
	docker push bongga/parrot-telegram-bot:0.0.1
 
delete:
	docker rmi -f bongga/parrot-telegram-bot:0.0.1
	docker container prune -f
	docker image prune -f

.PHONY: venv activate clean
