test:
	python -m unittest

build:
	python3 -m pip install --upgrade build
	python3 -m build

upload: build
	python3 -m twine upload --repository testpypi dist/*
	