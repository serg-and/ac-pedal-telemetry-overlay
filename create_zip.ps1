$app=$args[0]
$version=$args[1]

mkdir temp
mkdir temp\apps\python
cp -r $app temp\apps\python\$app
echo V${version} >> temp\apps\python\$app\RELEASE.txt
mkdir temp\content\gui\icons
cp -r icons\* temp\content\gui\icons
Compress-Archive temp\* ${app}_v${version}.zip
rm -r temp