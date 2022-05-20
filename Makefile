build:
	docker build -t twifavoritedl:latest .

run:
	docker run --rm $(ARGS) twifavoritedl:latest

authenticate:
	docker run --rm -it $(ARGS) twifavoritedl:latest gosu user python3 authenticate.py

