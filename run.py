from app import app
import os

print("It's time to start running")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)