from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKeyConstraint, Identity, Index, Integer, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Characteristics(Base):
    __tablename__ = 'characteristics'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='characteristics_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    product_characteristics: Mapped[list['ProductCharacteristics']] = relationship('ProductCharacteristics', back_populates='characteristic')


class OrderStatuses(Base):
    __tablename__ = 'order_statuses'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='order_statuses_pkey'),
        UniqueConstraint('name', name='unique_order_status_name')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='status')


class Products(Base):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('price >= 0::numeric', name='products_price_check'),
        CheckConstraint('stock >= 0', name='products_stock_check'),
        PrimaryKeyConstraint('id', name='products_pkey'),
        Index('idx_products_name', 'name')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String)

    product_characteristics: Mapped[list['ProductCharacteristics']] = relationship('ProductCharacteristics', back_populates='product')
    favorites: Mapped[list['Favorites']] = relationship('Favorites', back_populates='product')
    cart_items: Mapped[list['CartItems']] = relationship('CartItems', back_populates='product')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[list['Users']] = relationship('Users', back_populates='role')


class ProductCharacteristics(Base):
    __tablename__ = 'product_characteristics'
    __table_args__ = (
        ForeignKeyConstraint(['characteristic_id'], ['characteristics.id'], ondelete='CASCADE', name='fk_characteristic'),
        ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE', name='fk_product'),
        PrimaryKeyConstraint('id', name='product_characteristics_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    characteristic_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)

    characteristic: Mapped['Characteristics'] = relationship('Characteristics', back_populates='product_characteristics')
    product: Mapped['Products'] = relationship('Products', back_populates='product_characteristics')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE', name='fk_user_role'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        Index('idx_users_email', 'email')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    role: Mapped['Roles'] = relationship('Roles', back_populates='users')
    carts: Mapped[list['Carts']] = relationship('Carts', back_populates='user')
    favorites: Mapped[list['Favorites']] = relationship('Favorites', back_populates='user')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='user')


class Carts(Base):
    __tablename__ = 'carts'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_user_cart'),
        PrimaryKeyConstraint('id', name='carts_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='carts')
    cart_items: Mapped[list['CartItems']] = relationship('CartItems', back_populates='cart')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='cart')


class Favorites(Base):
    __tablename__ = 'favorites'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE', name='fk_product_fav'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_user_fav'),
        PrimaryKeyConstraint('id', name='favorites_pkey'),
        UniqueConstraint('user_id', 'product_id', name='unique_user_product_fav')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    product: Mapped['Products'] = relationship('Products', back_populates='favorites')
    user: Mapped['Users'] = relationship('Users', back_populates='favorites')


class CartItems(Base):
    __tablename__ = 'cart_items'
    __table_args__ = (
        CheckConstraint('quantity > 0', name='cart_items_quantity_check'),
        ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE', name='fk_cart'),
        ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE', name='fk_product_cart_item'),
        PrimaryKeyConstraint('id', name='cart_items_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    cart_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    cart: Mapped['Carts'] = relationship('Carts', back_populates='cart_items')
    product: Mapped['Products'] = relationship('Products', back_populates='cart_items')


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        CheckConstraint('total_amount >= 0::numeric', name='orders_total_amount_check'),
        ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE', name='fk_cart_order'),
        ForeignKeyConstraint(['status_id'], ['order_statuses.id'], name='fk_status_order'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_user_order'),
        PrimaryKeyConstraint('id', name='orders_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cart_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status_id: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    cart: Mapped['Carts'] = relationship('Carts', back_populates='orders')
    status: Mapped['OrderStatuses'] = relationship('OrderStatuses', back_populates='orders')
    user: Mapped['Users'] = relationship('Users', back_populates='orders')
