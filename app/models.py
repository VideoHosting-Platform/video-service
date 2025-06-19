from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base
from app.schemas import VideoReturn


class Video(Base):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    video_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    video_url: Mapped[str] = mapped_column(nullable=False)
    views: Mapped[int] = mapped_column(nullable=True, default=0)
    likes: Mapped[int]= mapped_column(nullable=True, default=0)
    dislikes: Mapped[int] = mapped_column(nullable=True, default=0)
    # author_fk: int = Field(alias="author_id")

    def to_return_model(self):
        return VideoReturn(
            id=self.id,
            title=self.title,
            video_url=self.video_url,
            video_id=self.video_id,
            views=self.views,
            likes=self.likes,
            dislikes=self.dislikes
        )
    def __str__(self): # человеко-читаемое представление
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"title={self.title!r},")
    
    def __repr__(self): # машинно-читаемое представление
        return str(self)

