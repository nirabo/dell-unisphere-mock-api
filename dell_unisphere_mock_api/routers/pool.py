from fastapi import APIRouter, HTTPException, Depends, Response
from typing import List

from dell_unisphere_mock_api.schemas.pool import Pool, PoolCreate, PoolUpdate
from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.core.auth import get_current_user

router = APIRouter()

pool_controller = PoolController()

@router.post("/types/pool/instances", response_model=Pool, status_code=201)
async def create_pool(pool: PoolCreate, _: dict = Depends(get_current_user)) -> Pool:
    """Create a new storage pool."""
    return pool_controller.create_pool(pool)

@router.get("/instances/pool/{pool_id}", response_model=Pool)
async def get_pool(pool_id: str, _: dict = Depends(get_current_user)) -> Pool:
    """Get a pool by ID."""
    pool = pool_controller.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool

@router.get("/instances/pool/name:{name}", response_model=Pool)
async def get_pool_by_name(name: str, _: dict = Depends(get_current_user)) -> Pool:
    """Get a pool by name."""
    pool = pool_controller.get_pool_by_name(name)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool

@router.get("/types/pool/instances", response_model=List[Pool])
async def list_pools(_: dict = Depends(get_current_user)) -> List[Pool]:
    """List all pools."""
    return pool_controller.list_pools()

@router.post("/instances/pool/{pool_id}/action/modify", response_model=Pool)
async def modify_pool(pool_id: str, pool_update: PoolUpdate, _: dict = Depends(get_current_user)) -> Pool:
    """Modify a pool."""
    pool = pool_controller.update_pool(pool_id, pool_update)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool

@router.delete("/instances/pool/{pool_id}", status_code=204)
async def delete_pool(pool_id: str, _: dict = Depends(get_current_user)):
    """Delete a pool."""
    success = pool_controller.delete_pool(pool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pool not found")

@router.delete("/instances/pool/name:{name}", status_code=204)
async def delete_pool_by_name(name: str, _: dict = Depends(get_current_user)):
    """Delete a pool by name."""
    pool = pool_controller.get_pool_by_name(name)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    pool_controller.delete_pool(pool.id)
    return Response(status_code=204)
