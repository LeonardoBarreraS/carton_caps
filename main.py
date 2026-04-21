import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from shell.api.app import create_app  # noqa: E402

app = create_app()
