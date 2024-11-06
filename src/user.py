from typing import List, TYPE_CHECKING
from flask_login import UserMixin
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from utils.sql import db

if TYPE_CHECKING:
    from .session import ChatbotSession


class User(UserMixin, db.Model): # typing: ignore
    id = db.Column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        db.String(250), unique=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        unique=True,
        nullable=False
    )

    profile_pic: Mapped[str] = mapped_column(
        db.String(250),
        nullable=False
    )

    sessions: Mapped[List["ChatbotSession"]] = relationship(
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        default_factory=list,
        order_by='ChatbotSession.created_at.desc()'
    )

    @property
    def latest_session(self) -> "ChatbotSession":
        """Get the latest session for this user"""
        from session import ChatbotSession # pylint: disable=import-outside-toplevel
        return db.session.execute(
            select(ChatbotSession).filter(ChatbotSession.user_id == self.id).order_by(ChatbotSession.created_at.desc()).limit(1)
        ).scalar()
