.PHONY: help clean clean-pyc clean-build list test test-dbg test-cov test-all coverage docs release sdist install deps develop tag

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
	@echo "test-dbg - run tests and debug with pdb"
	@echo "testloop - run tests in a loop"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"
	@echo "install - install"
	@echo "develop - install in development mode"
	@echo "deps - install dependencies"
	@echo "dev_deps - install dependencies for development"
	@echo "release - package a release in wheel and tarball"
	@echo "upload - make a release and run the scripts/deploy.sh"
	@echo "tag - create a git tag with current version"

install:
	pipenv run python setup.py install

develop: dev_deps
	pipenv run python setup.py develop

deps:
	pipenv install

dev_deps:
	pipenv install --dev

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
	pipenv run flake8 $(project-name)/

test:
	pipenv run py.test -v

test-cov:
	pipenv run py.test --cov-report term-missing --cov=$(project-name)

test-dbg:
	pipenv run py.test --pdb

testloop:
	pipenv run py.test -f

coverage:
	pipenv run pytest --cov=hansel
	pipenv run coverage report -m

build:
	pipenv run python setup.py sdist --formats gztar bdist_wheel upload

tag: clean
	@echo "Creating git tag v$(version)"
	git tag v$(version)
	git push --tags

release: clean build tag

patch:
	pipenv run bumpversion patch

minor:
	pipenv run bumpversion minor

major:
	pipenv run bumpversion major
