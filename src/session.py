from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from utils.sql import db

if TYPE_CHECKING:
    from .user import User


class ChatbotSession(db.Model): # type: ignore
    id = db.Column(db.Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        db.ForeignKey('user.id'),
        nullable=False,
        init=False
    )

    created_at: Mapped[str] = mapped_column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        init=False
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
    chat_history: Mapped[str] = mapped_column(db.Text, nullable=False, default="[]")
