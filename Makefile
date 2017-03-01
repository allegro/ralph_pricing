install:
	pip install -e .

quicktest:
	test_scrooge test ralph_scrooge

test-with-coveralls:
	coverage run --source=ralph_scrooge --omit='*migrations*,*tests*,*__init__*' '$(VIRTUAL_ENV)/bin/test_scrooge' test ralph_scrooge

coverage:
	make test-with-coveralls
	coverage report

flake:
	flake8 --exclude="migrations,settings" --statistics src/ralph_scrooge

runserver:
	dev_scrooge runserver 0.0.0.0:8000

install_ui:
	npm install
	./node_modules/.bin/gulp

clean:
	find . -name '*.py[cod]' -exec rm -rf {} \;
