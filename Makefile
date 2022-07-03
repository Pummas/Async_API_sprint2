
up:
	docker-compose -f tests/functional/docker-compose.yml up -d --build

down:
	docker-compose -f tests/functional/docker-compose.yml down
