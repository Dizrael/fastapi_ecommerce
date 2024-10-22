import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, insert, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import Product
from app.models.ratings import Rating
from app.models.reviews import Review
from app.routers.auth import get_current_user

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/all_reviews")
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found",
        )
    return reviews.all()

@router.get("/products_reviews")
async def get_products_reviews(
        db: Annotated[AsyncSession, Depends(get_db)],
        product_id: int
):
    reviews = await db.scalars(select(Review).where(Review.id == product_id))
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found",
        )
    return reviews.all()


@router.post("/add_review")
async def add_review(
        db: Annotated[AsyncSession, Depends(get_db)],
        review: str,
        rating: int,
        get_user: Annotated[dict, Depends(get_current_user)],
        product_id: int
):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only customers can add reviews",
        )
    else:
        product = await db.scalar(select(Product).where(Product.id == product_id))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        # Добавляем рейтинг
        await db.execute(insert(Rating).values(
            grade=rating,
            user_id=get_user.get('id'),
            product_id=product_id
        ))
        await db.commit()

        # Получаем id добавленного рейтинга
        rating_id = await db.scalar(select(Rating.id).where(and_(
            Rating.user_id == get_user.get('id'),
            Rating.product_id == product_id)
        ))

        # Добавляем отзыв
        await db.execute(insert(Review).values(
            review=review,
            rating_id=rating_id,  # Используйте rating_id
            product_id=product_id,
            comment_date=datetime.datetime.utcnow(),
            user_id=get_user.get('id'),
        ))
        await db.commit()

        # Пересчитываем средний рейтинг для продукта
        avg_rating = await db.scalar(select(func.avg(Rating.grade)).where(
            Rating.product_id == product_id,
            Rating.is_active == True
        ))

        # Обновляем рейтинг продукта
        await db.execute(update(Product).where(Product.id == product_id).values(rating=avg_rating))
        await db.commit()

        return {"status": status.HTTP_201_CREATED, "detail": "Review added"}


@router.delete("/delete_reviews")
async def delete_reviews(
        db: Annotated[AsyncSession, Depends(get_db)],
        review_id: int,
        get_user: Annotated[dict, Depends(get_current_user)],
):
    if get_user.get('is_admin'):
        review: Review = await db.scalar(select(Review).where(Review.id == review_id))
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Делаем неактивным отзыв и рейтинг
        await db.execute(update(Review).where(Review.id == review_id).values(is_active=False))
        await db.execute(update(Rating).where(Rating.id == review.rating_id).values(is_active=False))
        await db.commit()

        # Пересчитываем средний рейтинг для продукта
        avg_rating = await db.scalar(select(func.avg(Rating.grade)).where(
            Rating.product_id == review.product_id,
            Rating.is_active == True
        ))

        # Обновляем рейтинг продукта
        await db.execute(update(Product).where(Product.id == review.product_id).values(rating=avg_rating))
        await db.commit()

        return {
            "status": status.HTTP_200_OK,
            "detail": "Review deleted",
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admin can delete reviews",
        )


