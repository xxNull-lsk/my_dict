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

which dpkg >/dev/null 2>&1
if [ $? -eq 0 ]; then
    pyinstaller mydict.spec

    version=`./dist/mydict/mydict -v`
    rm -rf deb/opt/my_dict >/dev/null 2>&1
    mkdir -p deb/opt/my_dict >/dev/null
    cp ./LICENSE ./deb/opt/my_dict
    cp -rf dist/mydict/* deb/opt/my_dict/
    sed -i "s/^Version:.*/Version:${version}/g" deb/DEBIAN/control
    dpkg -b deb dist/mydict_linux_x64_${version}.deb
    rm -rf deb/opt/my_dict/*
    sed -i "s/^Version:.*/Version:0.0.0/g" deb/DEBIAN/control

else
    pyinstaller -y 我的词典.spec

    cd $DIR/dist
    version=`./我的词典 -v`
    cp ../LICENSE .
    source /etc/os-release
    tar -czf mydict_${ID}_linux_x64_${version}.tar.gz 我的词典 LICENSE

fi

