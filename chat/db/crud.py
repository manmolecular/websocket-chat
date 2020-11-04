from datetime import datetime

from argon2 import PasswordHasher
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from chat.db import models
from chat.db.base import SessionLocal

# Use argon2 password hasher
ph = PasswordHasher()


# Transform object to represent as dict
def object_as_dict(obj):
    if not obj:
        return obj
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


class DatabaseCrud:
    """
    Handle database
    """
    @staticmethod
    def create_user(
        username: str, password: str, db: Session = SessionLocal(), *args, **kwargs
    ) -> None:
        """
        Create user, hash password with Argon2
        :param username: username
        :param password: password
        :param db: session
        :param args: some args
        :param kwargs: some kwargs
        :return: None
        """
        try:
            password_hash = ph.hash(password)
            db_user = models.User(username=username, password=password_hash)
            db.add(db_user)
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def check_user_exists(
        username: str, db: Session = SessionLocal(), *args, **kwargs
    ) -> bool:
        """
        Check if user exists
        :param username: username
        :param db: session
        :param args: some args
        :param kwargs: some kwargs
        :return: True or False
        """
        try:
            db_user = (
                db.query(models.User).filter(models.User.username == username).first()
            )
            if db_user:
                return True
        except:
            return False
        finally:
            db.close()

    @staticmethod
    def check_credentials(
        username: str, password: str, db: Session = SessionLocal(), *args, **kwargs
    ) -> bool:
        """
        Check that credentials is correct, verify Argon2 hash
        :param username: username
        :param password: password
        :param db: session to use
        :param args: some args
        :param kwargs: some kwargs
        :return: True if correct, else False
        """
        try:
            db_user = (
                db.query(models.User).filter(models.User.username == username).first()
            )
            if db_user:
                return ph.verify(hash=db_user.password, password=password)
        except:
            return False
        finally:
            db.close()

    @staticmethod
    def save_message(
        username: str,
        message: str,
        date_time: datetime,
        db: Session = SessionLocal(),
        *args,
        **kwargs
    ) -> None:
        """
        Save user message
        :param username: username
        :param message: message
        :param date_time: date and time of the message
        :param db: session
        :param args: some args
        :param kwargs: some kwargs
        :return: None
        """
        try:
            if not message or not username:
                return
            user = (
                db.query(models.User).filter(models.User.username == username).first()
            )
            if not user:
                return
            user_id = user.user_id
            db_message = models.Message(
                owner_id=user_id, message=message, date_time=date_time
            )
            db.add(db_message)
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
