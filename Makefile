quicktest:
	DJANGO_SETTINGS_PROFILE=test-pricing ralph test ralph_pricing

test-with-coveralls:
	DJANGO_SETTINGS_PROFILE=test-pricing coverage run --source=ralph_pricing --omit='*migrations*,*tests*,*__init__*' '$(VIRTUAL_ENV)/bin/ralph' test ralph_pricing

coverage:
	make test-with-coveralls
	coverage html
	coverage report

flake:
	flake8 --exclude="migrations" --statistics src/ralph_pricing

runserver:
	ralph runserver
