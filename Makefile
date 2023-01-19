lint:
	isort .
	black .
	mypy .
	pflake8 .
