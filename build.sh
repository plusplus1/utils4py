#!/bin/sh

DIR=$(cd `dirname $0` ; pwd)
echo $DIR
cd $DIR

rm -rf ./dist/
python3 setup.py sdist bdist_wheel || true
rm -rf build *.egg-info

