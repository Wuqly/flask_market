# app/web/app.py
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from dotenv import load_dotenv
from .models import db


dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# Конфигурация
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL не задан!")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "super-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy + Migrate
db.init_app(app)

from .models import Users, Roles, Products, Characteristics, ProductCharacteristics, Carts, CartItems, Favorites, Orders, OrderStatuses

# Flask-Admin
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login"))

with app.app_context():
    db.create_all()
    admin = Admin(app, name="Shop Admin")
    admin.add_view(AdminModelView(Users, db.session))
    admin.add_view(AdminModelView(Roles, db.session))
    admin.add_view(AdminModelView(Products, db.session))
    admin.add_view(AdminModelView(Characteristics, db.session))
    admin.add_view(AdminModelView(ProductCharacteristics, db.session))
    admin.add_view(AdminModelView(Carts, db.session))
    admin.add_view(AdminModelView(CartItems, db.session))
    admin.add_view(AdminModelView(Favorites, db.session))
    admin.add_view(AdminModelView(Orders, db.session))
    admin.add_view(AdminModelView(OrderStatuses, db.session))

migrate = Migrate(app, db)

# Login
login_manager = LoginManager(app)
login_manager.login_view = "login"


# UserMixin обертка
class AuthUser(UserMixin):
    def __init__(self, user):
        self.id = str(user.id)
        self.username = user.username
        self.email = user.email
        self.role_name = getattr(user.role, "name", None)
        self._row = user

@login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(int(user_id))
    return AuthUser(user) if user else None

# Роуты
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = Users.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(AuthUser(user))
            return redirect(url_for("index"))
        else:
            flash("Неверный email или пароль")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# Создание админа (выполнять вручную)
def create_admin():
    admin_role = Roles.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Roles(name="admin")
        db.session.add(admin_role)
        db.session.commit()
    admin_user = Users.query.filter_by(email=os.getenv("ADMIN_EMAIL")).first()
    if not admin_user:
        admin_user = Users(
            username=os.getenv("ADMIN_USERNAME"),
            email=os.getenv("ADMIN_EMAIL"),
            role_id=admin_role.id
        )
        admin_user.set_password(os.getenv("ADMIN_PASSWORD"))
        db.session.add(admin_user)
        db.session.commit()
        print(f"Created admin {admin_user.email}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
