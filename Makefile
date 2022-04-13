python3_minor=9
version=3.$(python3_minor)

python=python$(version)
poetry_exe=$(python) -m poetry

install:
	$(poetry_exe) install

host_install:
	$(python) -m ensurepip --user
	$(python) -m pip install --user poetry

run:
	$(poetry_exe) run python get_episodes.py

poetry:
	@echo $(poetry_exe)


build: host_install install

check: build run
