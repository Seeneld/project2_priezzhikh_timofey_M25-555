install:
	poetry install

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

build:
	poetry build

lint:
	 poetry run ruff check .

database:
	poetry run database 