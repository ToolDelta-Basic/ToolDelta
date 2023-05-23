echo Starting to build ToolDelta executable file...
rm ToolDelta
pyinstaller -F ToolDelta.py
chmod u+x dist/ToolDelta
sudo mv dist/ToolDelta .
rm -rf build
rm ToolDelta.spec
echo Finished!
