.PHONY: help clean clean-pyc clean-build list test test-cov test-all coverage docs release sdist install deps develop tag

project-name = hansel

version-var := "__version__ = "
version-string := $(shell grep $(version-var) $(project-name)/version.py)
version := $(subst __version__ = ,,$(version-string))

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-cov - run tests with the default Python and report coverage"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "install - install"
	@echo "develop - install in development mode"
	@echo "deps - install dependencies"
	@echo "tag - create a git tag with current version"

install: install_deps
	python setup.py install

develop: install_deps
	python setup.py develop

deps:
	pip install -r requirements.txt

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.log*' -delete

lint:
	flake8 $(project-name) test

test:
	py.test

test-cov:
	py.test --cov-report term-missing --cov=$(project-name)

test-all:
	tox

coverage:
	coverage run --source $(project-name) setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/$(project-name).rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ $(project-name)
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

tag: clean
	@echo "Creating git tag v$(version)"
	git tag v$(version)
	git push --tags

release: clean tag
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	python setup.py bdist_wheel upload
	ls -l dist
