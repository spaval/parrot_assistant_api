.ONESHELL:
.DEFAULT_GOAL := run

clean:
	rm -rf node_modules
	rm -rf dist
	rm -f package-lock.json
	rm -f pnpm-lock.yaml

setup:
	pnpm install

dist: setup
	pnpm build

run:
	pnpm start

dev:
	pnpm dev

build:
	docker build --build-arg env_arg=pdn -t bongga/parrot-whatsapp-bot:0.0.1 -f config/Dockerfile .

docker:
	docker run -itd --name parrot-whatsapp-bot-container bongga/parrot-whatsapp-bot:0.0.1

deploy:
	docker push bongga/parrot-whatsapp-bot:0.0.1
 
delete:
	docker rmi -f bongga/parrot-whatsapp-bot:0.0.1
	docker container prune -f
	docker image prune -f

.PHONY: setup run