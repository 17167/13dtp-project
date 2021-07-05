import os

os.system("pip install -r requirements.txt -q")

from app import app

print("Database Initiated")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)