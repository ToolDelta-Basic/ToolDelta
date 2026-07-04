import subprocess
import os
import sys
from pathlib import Path

PYTHON_ROOT_PATH = Path(sys.prefix)
PROTOC_PATH = PYTHON_ROOT_PATH / Path("Lib/site-packages/grpc_tools/protoc.py")

this_dir = Path(os.path.dirname(__file__))

for file in os.listdir(this_dir / "proto"):
    if file.endswith(".proto"):
        subprocess.run([
            sys.executable,
            str(PROTOC_PATH),
            f"--python_out={this_dir.parent}",
            f"--grpc_python_out={this_dir.parent}",
            "-I", str(this_dir),
            str(this_dir / "proto" / file)
        ], check=True)

for file in os.listdir(this_dir):
    if file.endswith(".py") and file != "builder.py":
        with open(this_dir / file, encoding="utf-8") as f:
            content = f.read()
        content = content.replace("from proto import", "from . import")
        with open(this_dir / file, "w", encoding="utf-8") as f:
            f.write(content)
