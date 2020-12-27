@ECHO OFF

python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel

@REM python -m twine upload dist/*

CMD /k