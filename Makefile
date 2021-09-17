test:
	python -m unittest

coverage:
	coverage run -m unittest
	coverage xml
	coverage report
	
build:
	python3 -m pip install --upgrade build
	python3 -m build

upload: build
	python3 -m twine upload --repository testpypi dist/*
	
readme:
	bash build_readme.sh