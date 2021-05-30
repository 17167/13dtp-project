from app import app
import os

print("Better watch out better not cry")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)