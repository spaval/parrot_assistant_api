.PHONY: venv

venv:
	python3 -m venv venv

activate:
	source venv/bin/activate

deactivate:
	cd config
	deactivate
	cd ..

deps:
	pip3 install --no-cache-dir -r config/requirements.txt

run:
	uvicorn main:Parrot.app --host 0.0.0.0 --port 8000 --reload --loop asyncio --env-file config/.env

telegram:
	python3 bot.py

build:
	docker build --platform=linux/amd64 -t bongga/parrot:0.0.1.dev -f config/Dockerfile .

docker:
	docker run -itd --name parrot-container -p 8000:8000 bongga/parrot:0.0.1.dev

deploy:
	docker push bongga/parrot:0.0.1.dev
 
delete:
	docker rmi -f bongga/parrot:0.0.1.dev
	docker container prune -f
	docker image prune -f