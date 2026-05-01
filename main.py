import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from shell.api.app import create_app  # noqa: E402

app = create_app()

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False)

