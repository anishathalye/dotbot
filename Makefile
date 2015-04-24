.PHONY: clean lint

clean:
	find . -type f -name '*.py[cod]' -delete
	find . -type f -name '*.*~' -delete

lint: clean
	-flake8 .
