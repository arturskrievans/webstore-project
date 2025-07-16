from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, Boolean, Float, ForeignKey, DateTime, func


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    balance: Mapped[float] = mapped_column(default=10000.00)
    earned: Mapped[float] = mapped_column(default=0.00)
    spent:  Mapped[float] = mapped_column(default=0.00)
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    products: Mapped[list["Product"]] = relationship(
        backref="seller", cascade="all, delete", lazy=True
    )
    purchases: Mapped[list["Purchase"]] = relationship(
        backref="buyer", cascade="all, delete", lazy=True
    )


class Product(db.Model):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    picture: Mapped[str] = mapped_column(String(50), default="default.jpg")
    description: Mapped[str] = mapped_column(Text)
    sold: Mapped[bool] = mapped_column(Boolean, default=False)
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modified: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)


class Purchase(db.Model):
    __tablename__ = 'purchase'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    product: Mapped["Product"] = relationship(
        backref="purchased", lazy=True
    )


class Message(db.Model):
    __tablename__ = 'message'

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(
        backref="messages", lazy=True
    )