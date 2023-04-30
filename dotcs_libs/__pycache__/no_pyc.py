import os, shutil
for file in os.listdir():
    print(file)
    if file.endswith(".pyc"):
        shutil.copy(file, file.replace(".cpython-310", ""))
        