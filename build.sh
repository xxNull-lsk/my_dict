pyinstaller 我的词典.spec

cd dist
version=`./我的词典 -v`
cp -f 我的词典 ../deb/opt/my_dict
cp ../LICENSE .
tar -czf my_dict_linux_x64_${version}.tar.gz 我的词典 LICENSE

cd ..
cp LICENSE deb/opt/my_dict
dpkg -b deb dist/mydict_linux_x64_${version}.deb
rm deb/opt/my_dict/我的词典
rm deb/opt/my_dict/LICENSE
