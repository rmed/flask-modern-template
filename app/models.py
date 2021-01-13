# -*- coding: utf-8 -*-

"""Database model definitions."""

import datetime
import time
from typing import Optional

import sqlalchemy
from flask_login import UserMixin
from passlib.pwd import genword

from . import db, user_hasher


class Invitation(db.Model):
    """User invitation.

    Attributes:
        id (int): ID of the invitation.
        owner_id (int): ID of the owner of the invite.
        user_id (int): ID of the user that signed up using this invite.
        token (str): Token used to signup.
        expiration (datetime): Date at which the invitation is no longer valid.
    """
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'users.id',
            name='fk_invitation_users_owner',
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'users.id',
            name='fk_invitation_users_user',
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        nullable=True
    )
    token = db.Column(
        db.String(64),
        nullable=False,
        default=genword(length=64),
        unique=True
    )
    expiration = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow()+datetime.timedelta(weeks=1),
        # If the server supports it:
        # server_default=sqlalchemy.sql.expression.text('NOW() + INTERVAL \'1 week\'')
    )

    # Relationships
    owner = db.relationship(
        'User',
        primaryjoin=('Invitation.owner_id == User.id')
    )

    user = db.relationship(
        'User',
        primaryjoin=('Invitation.user_id == User.id')
    )

    @classmethod
    def get_by_token(cls, token: str) -> Optional['Invitation']:
        """Obtain an already existing invitation by token.

        Args:
            token (str): Token of the invitation.

        Returns:
            Invitation instance or `None` if not found.
        """
        return cls.query.filter_by(token=token).first()

    @classmethod
    def generate_token(cls) -> str:
        """Generate a random token for the invitation.

        Returns:
            Random token.
        """
        return genword(length=64)


class User(db.Model, UserMixin):
    """User definition.

    Attributes:
        id (int): User ID.
        username (str): Username, must be unique.
        password (str): Encrypted password.
        email (str): Email of the user, must be unique.
        is_active (bool): Whether the user is active (can login).
        locale (str): Locale code.
        timezone (str): Timezone used to localize dates.
        invitations (int): Remaining invitations for this user.
        serial (str): Serial for sessions.
        joined_at (datetime): Date at which the user joined.
        password_reset_token (str): Unique token used to reset the password.
        password_reset_expiration (datetime): Date at which the password reset
            token expires.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Authentication
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    email = db.Column(db.String(255), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, nullable=False,
                          default=False, server_default='f')

    # Additional attributes
    locale = db.Column(db.String(2), nullable=False,
                       default='en', server_default='en')
    timezone = db.Column(db.String(50), nullable=False,
                         default='UTC', server_default='UTC')
    invitations = db.Column(db.Integer, nullable=False,
                            default=10, server_default='10')
    serial = db.Column(db.Text, nullable=False,
                       default=lambda: User.generate_serial())

    joined_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.utcnow(),
                          server_default=sqlalchemy.sql.func.now())
    password_reset_token = db.Column(db.String(100), nullable=True, unique=True)
    password_reset_expiration = db.Column(db.DateTime, nullable=True)

    @property
    def hashid(self) -> str:
        """Calculate the Hashid from user ID."""
        return user_hasher.encode(self.id)

    @staticmethod
    def generate_serial(length: int = 5) -> str:
        """Generate a valid session serial.

        A serial is comprised of the current timestamp and N random characters.

        Args:
            length (int): Length for the random string appended to the timestamp.

        Returns:
            Serial string.
        """
        return '{}{}'.format(int(time.time()), genword(length=length))

    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Obtain an already existing user by username.

        Args:
            username (str): Unique username of the user

        Returns:
            User instance or None if not found.
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Obtain an already existing user by email.

        Args:
            email (str): Unique email of the user

        Returns:
            User instance or None if not found.
        """
        return cls.query.filter_by(email=email).first()

    def get_id(self) -> str:
        """Return the ID to use for the login manager.

        This is generated by concatenating the numerical ID and the serial
        in order to allow invalidating user sessions on certain scenarios
        such as password change.

        Returns:
            ID to use for session tokens.
        """
        return '{}_{}'.format(self.id, self.serial)
