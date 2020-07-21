
build:
	docker-compose build

up:
	docker-compose up -d

test:
	docker exec py01 /bin/sh -c "python app-test.py"  

shell-py:
	docker exec -ti py01 bash

