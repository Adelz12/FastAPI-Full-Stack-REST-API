import json
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Item, User
from app.schemas import ItemCreate, ItemOut
from app.deps import get_current_user, get_redis

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """Create a new item for the authenticated user and invalidate their items cache."""
    new_item = Item(
        title=item_in.title,
        description=item_in.description,
        owner_id=current_user.id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    # Cache Invalidation: Delete the cached item list for this user
    cache_key = f"user:{current_user.id}:items"
    try:
        await redis.delete(cache_key)
    except Exception:
        # Soft-fail caching operations so that core DB writes are never blocked
        pass

    return new_item

@router.get("/", response_model=list[ItemOut])
async def list_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis)
):
    """Retrieve all items owned by the authenticated user. Caches results in Redis for 60 seconds."""
    cache_key = f"user:{current_user.id}:items"

    # Attempt to load from Redis cache
    try:
        cached_data = await redis.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
    except Exception:
        # Gracefully fall back to DB if Redis is temporarily offline
        pass

    # Query items from Database
    stmt = select(Item).where(Item.owner_id == current_user.id)
    result = await db.execute(stmt)
    items = result.scalars().all()

    # Serialize to standard dictionary format for JSON storage
    items_serialized = [ItemOut.model_validate(item).model_dump() for item in items]

    # Save data back to Redis with a 60-second TTL (Time to Live)
    try:
        await redis.setex(cache_key, 60, json.dumps(items_serialized))
    except Exception:
        # Ignore write failures to ensure service availability
        pass

    return items_serialized
