# E.g., FACTLOG_TOX_OPTS=-e py27
FACTLOG_TOX_OPTS ?=

.PHONY: test clean cog upload

## Testing
test:
	tox $(FACTLOG_TOX_OPTS)

clean:
	rm -rf *.egg-info .tox MANIFEST

## Update files using cog.py
cog: factlog/__init__.py
factlog/__init__.py: README.rst
	cd factlog && cog.py -r __init__.py

## Upload to PyPI
upload: cog
	python setup.py register sdist upload
