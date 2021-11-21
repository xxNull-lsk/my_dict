#!/bin/bash

SOURCE="$0"
while [ -h "$SOURCE"  ]; do
        DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd  )"
        SOURCE="$(readlink "$SOURCE")"
        [[ $SOURCE != /*  ]] && SOURCE="$DIR/$SOURCE"
done
DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd  )"

cd $DIR
rm -rf dist/mydict
pyinstaller mydict.spec

version=`./dist/mydict/mydict -v`

rm -rf deb/opt/my_dict/* >/dev/null
cp ./LICENSE ./deb/opt/my_dict
cp -rf dist/mydict/* deb/opt/my_dict/
sed -i "s/^Version:.*/Version:${version}/g" deb/DEBIAN/control
dpkg -b deb dist/mydict_linux_x64_${version}.deb
rm -rf deb/opt/my_dict/*
sed -i "s/^Version:.*/Version:0.0.0/g" deb/DEBIAN/control

cd $DIR
pyinstaller -y 我的词典.spec

cd dist
version=`./我的词典 -v`
cp ../LICENSE .
tar -czf my_dict_linux_x64_${version}.tar.gz 我的词典 LICENSE
