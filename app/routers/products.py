from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify

from app.backend.db_depends import get_db
from app.models import Category, Product
from app.schemas import CreateProduct
from app.routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no products")
    return products.all()


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)],
                         product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    category = await db.scalar(select(Category).where(Category.id == product.category))
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        await db.execute(insert(Product).values(
            name=product.name,
            slug=slugify(product.name),
            description=product.description,
            price=product.price,
            image_url=product.image_url,
            category_id=product.category,
            stock=product.stock,
            rating=0.0,
            supplier_id=get_user.get('id')))
        await db.commit()
        return {
            "status_code": status.HTTP_201_CREATED,
            "transaction": "Successful"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not allowed to create products"
        )


@router.get('/{category_slug}')
async def product_by_category(category_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    subcategories = await db.scalars(select(Category.id).where(Category.parent_id == category.id))
    categories = [category.id] + [i.id for i in subcategories.all()]
    products = await db.scalars(select(Product).where(
        Product.category_id.in_(categories), Product.is_active == True, Product.stock > 0
    ))
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no products in this category")

    return products.all()


@router.get('/detail/{product_slug}', status_code=status.HTTP_200_OK)
async def product_detail(product_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    product = await db.execute(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no product found"
        )
    return product.first()


@router.put('/detail/{product_slug}')
async def update_product(
        product_slug: str,
        db: Annotated[AsyncSession, Depends(get_db)],
        new_product: CreateProduct,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no product found"
        )
    category = await db.scalar(select(Category).where(Category.id == new_product.category))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == new_product.supplier_id or get_user.get('is_admin'):
            await db.execute(
                update(Product).where(Product.slug == product_slug)
                .values(name=new_product.name,
                        description=new_product.description,
                        price=new_product.price,
                        image_url=new_product.image_url,
                        stock=new_product.stock,
                        category_id=new_product.category,
                        slug=slugify(new_product.name)))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'
            }
        else:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )



@router.delete('/delete')
async def delete_product(product_slug: str,
                         db: Annotated[AsyncSession, Depends(get_db)],
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin'):
            await db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to use this method'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to use this method'
        )
