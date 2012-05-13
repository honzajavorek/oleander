
install:
	pip install -r requirements.txt --upgrade

sass:
	sass --style compressed --update oleander/static/css:oleander/static/css

clean:
	-rm -rf .sass-cache
	find . -type f -name '*.pyc' | xargs rm
