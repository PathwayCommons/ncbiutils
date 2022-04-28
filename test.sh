#! /bin/bash
poetry run pytest tests --cov ./ncbiutils
poetry run flake8 ./ncbiutils --count --select=E9,F63,F7,F82 --show-source --statistics
poetry run flake8 ./ncbiutils --count --exit-zero --max-complexity=10 --statistics
poetry run mypy . --cache-dir=/dev/null

