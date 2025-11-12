# app/web/models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import decimal

db = SQLAlchemy()

# =========================
# Роли
# =========================
class Roles(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    users = db.relationship("Users", back_populates="role")


# =========================
# Пользователи
# =========================
class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    role = db.relationship("Roles", back_populates="users")
    carts = db.relationship("Carts", back_populates="user")
    favorites = db.relationship("Favorites", back_populates="user")
    orders = db.relationship("Orders", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =========================
# Продукты
# =========================
class Products(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, index=True)
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    product_characteristics = db.relationship("ProductCharacteristics", back_populates="product")
    favorites = db.relationship("Favorites", back_populates="product")
    cart_items = db.relationship("CartItems", back_populates="product")


# =========================
# Характеристики
# =========================
class Characteristics(db.Model):
    __tablename__ = "characteristics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    product_characteristics = db.relationship("ProductCharacteristics", back_populates="characteristic")


# =========================
# Связь Продукт-Характеристика
# =========================
class ProductCharacteristics(db.Model):
    __tablename__ = "product_characteristics"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    characteristic_id = db.Column(db.Integer, db.ForeignKey("characteristics.id", ondelete="CASCADE"), nullable=False)
    value = db.Column(db.String, nullable=False)

    product = db.relationship("Products", back_populates="product_characteristics")
    characteristic = db.relationship("Characteristics", back_populates="product_characteristics")


# =========================
# Корзины
# =========================
class Carts(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("Users", back_populates="carts")
    cart_items = db.relationship("CartItems", back_populates="cart")
    orders = db.relationship("Orders", back_populates="cart")


# =========================
# Элементы корзины
# =========================
class CartItems(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    cart = db.relationship("Carts", back_populates="cart_items")
    product = db.relationship("Products", back_populates="cart_items")


# =========================
# Избранное
# =========================
class Favorites(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("Users", back_populates="favorites")
    product = db.relationship("Products", back_populates="favorites")


# =========================
# Статусы заказов
# =========================
class OrderStatuses(db.Model):
    __tablename__ = "order_statuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    orders = db.relationship("Orders", back_populates="status")


# =========================
# Заказы
# =========================
class Orders(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("order_statuses.id"), nullable=False)
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("Users", back_populates="orders")
    cart = db.relationship("Carts", back_populates="orders")
    status = db.relationship("OrderStatuses", back_populates="orders")
