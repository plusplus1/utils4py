.PHONY: clean
clean:
	rm -rf ./dist/
	rm -rf build *.egg-info

.PHONY: fmt
fmt:
	autopep8 --max-line-length=300 -a -a -i $$(git status -s |grep ".py$$" |grep -v "^D" |awk '{print $$NF}' | xargs)

.PHONY: build
build: clean build_py2 build_py3

.PHONY: build_py2 
build_py2: clean
	python2.7 setup.py sdist bdist_wheel || true
	rm -rf build *.egg-info dist/*.tar.gz

.PHONY: build_py3
build_py3: clean
	python3 setup.py sdist bdist_wheel || true
	rm -rf build *.egg-info dist/*.tar.gz

.PHONY: pip
pip:
	pip install -r requires.txt
	pip install pytest

.PHONY: test
test:
	PYTHONPATH=./ pytest -s -v
