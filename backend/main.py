import atexit
import os

from app import login, passkey_auth, passkey_reg, users
from app.db import save_userdb
from app.users import User
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)

# flask_login setup
login_manager = LoginManager()
login_manager.init_app(app)


# user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


app.register_blueprint(login.bp)
app.register_blueprint(users.bp)
app.register_blueprint(passkey_auth.bp)
app.register_blueprint(passkey_reg.bp)

RP_ID = os.getenv("RP_ID")
EXPECTED_ORIGIN = os.getenv("EXPECTED_ORIGIN")


## debugging purpose only
def teardown():
    save_userdb()
    print("** UserDB saved on exit/reload.")


if __name__ == "__main__":
    atexit.register(teardown)
    app.run(port=8000, debug=True)
