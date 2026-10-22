import sys
import subprocess
import uvicorn
from book_ai.config import DATA_DIR

def main():
    if "--test" in sys.argv:
        print("Running Book AI automated test suite...")
        res = subprocess.run([sys.executable, "-m", "pytest", "-v", "tests/test_suite.py"])
        sys.exit(res.returncode)

    print(f"Book AI Data Directory: {DATA_DIR}")
    print("Starting Book AI Local Server on [http://127.0.0.1:8000](http://127.0.0.1:8000) ...")
    uvicorn.run("book_ai.backend.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
