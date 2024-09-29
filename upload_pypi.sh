mkdir -p dist
rm -rf dist/*
python setup.py sdist build
pip install twine --index-url https://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com
twine upload dist/*
