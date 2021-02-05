del dist\* /Q && python setup.py pytest && python setup.py sdist && twine upload dist/*.tar.gz
pause