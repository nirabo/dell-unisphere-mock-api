from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import JSONResponse

from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.config import settings
from dell_unisphere_mock_api.schemas.pool import Pool, PoolAutoConfigurationResponse, PoolCreate, PoolUpdate

router = APIRouter()

pool_controller = PoolController()


@router.post("/types/pool/instances", response_model=Pool | dict, status_code=201)
async def create_pool(
    pool: PoolCreate, timeout: Optional[int] = Query(None), _: dict = Depends(get_current_user)
) -> Pool | dict:
    """Create a new storage pool."""
    # If timeout=0, handle as async request
    if timeout == 0:
        from dell_unisphere_mock_api.controllers.job_controller import JobController
        from dell_unisphere_mock_api.schemas.job import JobCreate, JobTask

        # Create a job for async pool creation
        job_controller = JobController()
        job_data = JobCreate(
            description=f"Create pool {pool.name}",
            tasks=[JobTask(name="CreatePool", object="pool", action="create", parametersIn=pool.model_dump())],
        )
        job = await job_controller.create_job(job_data)
        return JSONResponse(status_code=202, content={"id": job.id})

    # Handle synchronous request
    return pool_controller.create_pool(pool)


@router.get("/instances/pool/name:{name}", response_model=Pool)
async def get_pool_by_name(name: str, _: dict = Depends(get_current_user)) -> Pool:
    """Get a pool by name."""
    pool = pool_controller.get_pool_by_name(name)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool


@router.get("/instances/pool/{pool_id}", response_model=Pool)
async def get_pool(pool_id: str, _: dict = Depends(get_current_user)) -> Pool:
    """Get a pool by ID."""
    pool = pool_controller.get_pool(pool_id)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool


@router.get("/types/pool/instances")
async def list_pools(
    _: dict = Depends(get_current_user),
    compact: bool = Query(False),
    fields: Optional[str] = Query(None),
    page: Optional[int] = Query(1),
    per_page: Optional[int] = Query(2000),
    orderby: Optional[str] = Query(None),
) -> JSONResponse:
    """List all pools with filtering and pagination."""
    pools = pool_controller.list_pools()

    # Apply sorting if specified
    if orderby:
        field, direction = orderby.split(" ") if " " in orderby else (orderby, "asc")
        reverse = direction.lower() == "desc"
        pools = sorted(pools, key=lambda x: getattr(x, field), reverse=reverse)

    # Apply pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    pools = pools[start_idx:end_idx]

    # Format response according to fields parameter
    if fields:
        field_list = fields.split(",")
        entries = []
        for pool in pools:
            content = {}
            for field in field_list:
                if hasattr(pool, field):
                    value = getattr(pool, field)
                    if isinstance(value, datetime):
                        content[field] = value.isoformat()
                    else:
                        content[field] = value
            entries.append({"content": content})
    else:
        # Use model_dump with custom datetime encoder
        entries = []
        for pool in pools:
            pool_dict = pool.model_dump()
            # Convert datetime objects to ISO format strings
            for key, value in pool_dict.items():
                if isinstance(value, datetime):
                    pool_dict[key] = value.isoformat()
            entries.append({"content": pool_dict})

    response_data = {
        "@base": f"{settings.API_BASE_URL}/types/pool/instances",
        "updated": datetime.now(timezone.utc).isoformat(),
        "links": [{"rel": "self", "href": f"&page={page}"}],
        "entries": entries,
    }

    return JSONResponse(content=response_data)


@router.patch("/instances/pool/{pool_id}", response_model=Pool)
async def modify_pool(pool_id: str, pool_update: PoolUpdate, _: dict = Depends(get_current_user)) -> Pool:
    """Modify a pool."""
    pool = pool_controller.update_pool(pool_id, pool_update)
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool


@router.delete("/instances/pool/name:{name}", status_code=204)
async def delete_pool_by_name(name: str, _: dict = Depends(get_current_user)):
    """Delete a pool by name."""
    success = pool_controller.delete_pool_by_name(name)
    if not success:
        raise HTTPException(status_code=404, detail="Pool not found")
    return Response(status_code=204)


@router.delete("/instances/pool/{pool_id}", status_code=204)
async def delete_pool(pool_id: str, _: dict = Depends(get_current_user)):
    """Delete a pool."""
    success = pool_controller.delete_pool(pool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pool not found")
    return Response(status_code=204)


@router.post("/types/pool/action/recommendAutoConfiguration", response_model=List[PoolAutoConfigurationResponse])
async def recommend_auto_configuration(_: dict = Depends(get_current_user)) -> List[PoolAutoConfigurationResponse]:
    """Get recommended pool configurations based on available drives."""
    # Check if there are existing pools
    pools = pool_controller.list_pools()
    if pools:
        raise HTTPException(
            status_code=400, detail="Auto configuration is only available when no pools exist on the system"
        )

    return pool_controller.recommend_auto_configuration()
