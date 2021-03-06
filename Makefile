all: test

prepare_test_env:
	docker run --name test_mysql --rm -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=letmein mysql:5.7
	docker run --name test_redis --rm -d -p 6379:6379 redis:5
	sleep 20 # waiting for services ready
	docker exec -ti test_mysql mysql -u root -pletmein -e 'create database flask_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
	docker exec -ti test_mysql mysql -u root -pletmein -e 'create database flask_demo_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'
	pip install -U -r requirements.txt
	pip install -U -r test_requirements.txt

test:
	black . --check
	flake8 app tests
	mypy --ignore-missing-imports app tests
	pytest	

server:
	gunicorn app:app -c gunicorn.py

destory_test_env:
	docker stop test_mysql test_redis
