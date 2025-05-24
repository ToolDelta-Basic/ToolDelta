import os
import sys
from pathlib import Path

PROTOC_PATH = Path(
    "C:/Users/25286/AppData/Local/Programs/Python/Python311/Lib/site-packages/grpc_tools/protoc.py"
)

this_dir = Path(os.path.dirname(__file__))

for file in os.listdir(this_dir / "proto"):
    if file.endswith(".proto"):
        os.system(
            f"{sys.executable} {PROTOC_PATH} --python_out={os.path.dirname(this_dir)} --grpc_python_out={os.path.dirname(this_dir)} -I {this_dir} {this_dir / 'proto' / file}"
        )

for file in os.listdir(this_dir):
    if file.endswith(".py") and file != "builder.py":
        with open(this_dir / file, encoding="utf-8") as f:
            content = f.read()
        content = content.replace("from proto import", "from . import")
        with open(this_dir / file, "w", encoding="utf-8") as f:
            f.write(content)
