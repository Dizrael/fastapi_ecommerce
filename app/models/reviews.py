from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating_id = Column(Integer, ForeignKey('ratings.id'))
    comment = Column(String)
    comment_date = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    product = relationship('Product', back_populates='reviews')
    rating = relationship('Rating')
    user = relationship('User', back_populates='reviews')
