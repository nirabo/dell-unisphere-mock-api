import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

from dell_unisphere_mock_api.controllers.pool_controller import PoolController
from dell_unisphere_mock_api.core.auth import get_current_user
from dell_unisphere_mock_api.core.config import settings
from dell_unisphere_mock_api.core.response import UnityResponseFormatter
from dell_unisphere_mock_api.core.response_models import ApiResponse
from dell_unisphere_mock_api.schemas.pool import Pool, PoolAutoConfigurationResponse, PoolCreate, PoolUpdate

router = APIRouter()

pool_controller = PoolController()


@router.post("/types/pool/instances", status_code=201)
async def create_pool(
    request: Request, pool: PoolCreate, timeout: Optional[int] = Query(None), _: dict = Depends(get_current_user)
) -> ApiResponse[Pool]:
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

        # Create a proper Unity API response
        formatter = UnityResponseFormatter(request)
        response = formatter.format_collection(
            [job], entry_links={0: [{"rel": "self", "href": f"/api/types/job/instances/{job.id}"}]}
        )
        return JSONResponse(status_code=202, content=response.model_dump(by_alias=True))

    # Handle synchronous request
    response = await pool_controller.create_pool(pool, request)
    # Get the pool ID from the response content
    pool_id = response.entries[0].content.id if response.entries else None
    # Add self link to the response
    if pool_id:
        response.entries[0].links = [{"rel": "self", "href": f"/api/types/pool/instances/{pool_id}"}]
    # Use model_dump with exclude_none to properly handle datetime serialization
    return JSONResponse(
        status_code=201,
        content=response.model_dump(by_alias=True, exclude_none=True),
        headers={"Content-Type": "application/json"},
    )


@router.get("/instances/pool/name:{name}")
async def get_pool_by_name(request: Request, name: str, _: dict = Depends(get_current_user)) -> ApiResponse[Pool]:
    """Get a pool by name."""
    return await pool_controller.get_pool_by_name(name, request)


@router.get("/instances/pool/{pool_id}")
async def get_pool(request: Request, pool_id: str, _: dict = Depends(get_current_user)) -> ApiResponse[Pool]:
    """Get a pool by ID."""
    return await pool_controller.get_pool(pool_id, request)


@router.get("/types/pool/instances")
async def list_pools(
    request: Request,
    compact: bool = Query(False),
    fields: Optional[str] = Query(None),
    page: Optional[int] = Query(1),
    per_page: Optional[int] = Query(2000),
    orderby: Optional[str] = Query(None),
    _: dict = Depends(get_current_user),
) -> ApiResponse[List[Pool]]:
    """List all pools with filtering and pagination."""
    return await pool_controller.list_pools(request, compact, fields, page, per_page, orderby)


@router.patch("/instances/pool/{pool_id}")
async def modify_pool(
    request: Request, pool_id: str, pool_update: PoolUpdate, _: dict = Depends(get_current_user)
) -> ApiResponse[Pool]:
    """Modify a pool."""
    return await pool_controller.update_pool(pool_id, pool_update, request)


@router.delete("/instances/pool/name:{name}", status_code=204)
async def delete_pool_by_name(request: Request, name: str, _: dict = Depends(get_current_user)) -> None:
    """Delete a pool by name."""
    await pool_controller.delete_pool_by_name(name, request)
    return Response(status_code=204)


@router.delete("/instances/pool/{pool_id}", status_code=204)
async def delete_pool(request: Request, pool_id: str, _: dict = Depends(get_current_user)) -> None:
    """Delete a pool."""
    await pool_controller.delete_pool(pool_id, request)
    return Response(status_code=204)


@router.get("/types/pool/action/recommendAutoConfiguration")
async def recommend_auto_configuration(
    request: Request, _: dict = Depends(get_current_user)
) -> ApiResponse[PoolAutoConfigurationResponse]:
    """Get recommended pool configurations based on available drives."""
    return await pool_controller.recommend_auto_configuration(request)
