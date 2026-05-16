install:
	pip install -r requirements.txt

run:
	@python3 main.py map.txt

debug:
	@python3 -m pdb main.py map.txt

clean:
	@find -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache

lint:
	python3 -m flake8 .
	python3 -m  mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
