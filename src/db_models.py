from datetime import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer, DateTime, Boolean
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
# from src.database import Base

##TODO
## relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    user_name = mapped_column(String(50), nullable=True, unique=True)
    password = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, user_name={self.user_name!r}, " \
               f"password={self.password!r})"


class Customer(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "customers"
    id = mapped_column(Integer, primary_key=True)
    email_address = mapped_column(String(50), nullable=False)
    name = mapped_column(String(50), nullable=True)
    # sender = relationship("Mail", back_populates="sender_user")
    # recipient = relationship("Mail", back_populates="recipient_user")

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
    # has_text = mapped_column(Boolean, nullable=False, default=False)
    # has_html = mapped_column(Boolean, nullable=False, default=False)
    # has_attachment = mapped_column(Boolean, nullable=False, default=False)

    # user: Mapped["Customer"] = relationship(back_populates="sender")

    def __repr__(self) -> str:
        return f"Emails(id={self.id!r}, sender={self.sender!r}, recipient={self.recipient!r}, " \
               f"time={self.time!r}, server_id={self.mail_server_id!r}, keyword={self.keyword!r})"


if __name__ == '__main__':

    from sqlalchemy import create_engine

    engine = create_engine("sqlite://", echo=True)
    # engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
    Base.metadata.create_all(engine)

    from sqlalchemy.orm import Session
    with Session(engine) as session:
        spongebob = Customer(
            email_address="spongebob@sqlalchemy.org",
        )
        sandy = Customer(
            email_address="sandy@sqlalchemy.org",
        )
        mail = Mail(
            sender='spongebob',
            recipient=1,
            time=datetime.now(),
            mail_server_id="aa",
            keyword="aa"
        )
        session.add_all([spongebob, sandy, mail])
        session.commit()

    from sqlalchemy import select
    session = Session(engine)
    stmt = select(Customer).where(Customer.email_address.in_(["spongebob@sqlalchemy.org", "sandy@sqlalchemy.org"]))
    for user in session.scalars(stmt):
        print(user)
    stmt = select(Mail)
    for mail in session.scalars(stmt):
        print(mail)