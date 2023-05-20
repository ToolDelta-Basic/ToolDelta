echo start
rm ToolDelta
pyinstaller -F ToolDelta.py
chmod u+x dist/ToolDelta
sudo mv dist/ToolDelta .