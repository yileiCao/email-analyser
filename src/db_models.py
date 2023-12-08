from datetime import datetime
from sqlalchemy import ForeignKey, Integer, DateTime, Boolean
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    user_name = mapped_column(String(50), nullable=True, unique=True)
    password = mapped_column(String(128), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, user_name={self.user_name!r}, " \
               f"password={self.password!r})"


class Customer(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "customers"
    id = mapped_column(Integer, primary_key=True)
    email_address = mapped_column(String(50), nullable=False)
    name = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"Customer(id={self.id!r}, email_address={self.email_address!r}, " \
               f"name={self.name!r})"


def same_as(column_name):
    def default_function(context):
        return context.current_parameters.get(column_name)
    return default_function


class Mail(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "mails"
    id = mapped_column(Integer, primary_key=True)
    sender = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    recipient = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    time = mapped_column(DateTime, nullable=False)
    mail_server_id = mapped_column(String(50), nullable=False)
    mail_thread_id = mapped_column(String(50), nullable=False, default=same_as('mail_server_id'))
    subject = mapped_column(String(200), nullable=True)
    keyword = mapped_column(String(200), nullable=True)
    owner = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    is_public = mapped_column(Boolean, nullable=False, default=False)
    sender_user = relationship("Customer", primaryjoin=sender == Customer.id)
    recipient_user = relationship("Customer", primaryjoin=recipient == Customer.id)
    mail_owner = relationship("User", primaryjoin=owner == User.id)

    def __repr__(self) -> str:
        return f"Emails(id={self.id!r}, sender={self.sender!r}, recipient={self.recipient!r}, " \
               f"time={self.time!r}, server_id={self.mail_server_id!r}, keyword={self.keyword!r})"


