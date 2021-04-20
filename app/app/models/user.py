import sqlalchemy as sa
from ..db.base_class import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.BigInteger, primary_key=True)
    username = sa.Column(sa.String(60))
    password = sa.Column(sa.String(128))
    is_admin = sa.Column(sa.Boolean, default=False)
    is_active = sa.Column(sa.Boolean, default=True)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(
                    sa.DateTime,
                    default=datetime.now,
                    onupdate=datetime.now
                )

    def __repr__(self):
        return f"<User {self.id}>"
