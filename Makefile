install:
	pip install -e . --use-mirrors --allow-all-external --allow-unverified ipaddr --allow-unverified postmarkup --allow-unverified python-graph-core --allow-unverified pysphere

quicktest:
	DJANGO_SETTINGS_MODULE=ralph_scrooge.settings-test-scrooge scrooge test ralph_scrooge

test-with-coveralls:
	DJANGO_SETTINGS_DIR=src/ralph_scrooge DJANGO_SETTINGS_PROFILE=test-scrooge coverage run --source=ralph_scrooge --omit='*migrations*,*tests*,*__init__*' '$(VIRTUAL_ENV)/bin/scrooge' test ralph_scrooge

coverage:
	make test-with-coveralls
	coverage html
	coverage report

flake:
	flake8 --exclude="migrations" --statistics src/ralph_scrooge

runserver:
	ralph runserver

install_ui:
	npm install
	./node_modules/.bin/gulp
