from fastapi import APIRouter, HTTPException, Request
from typing import Any, Dict, List

from caching.sqlite_cache import cache

router = APIRouter()


@router.delete("/remove")
def delete_vin_from_cache(request: Request) -> Dict[str, Any]:
    """
    Deletes the vin from the cache, if present, and returns a response indicating success or failure.

    :param Request request: The FastAPI request object.
    :return: A dictionary containing the vin and the cache deletion status.
    :rtype: dict
    :raises HTTPException 400: If the VIN is not a 17-character alphanumeric string.
    """
    vin = request.query_params.get("vin", "")
    if not len(vin) == 17 or not vin.isalnum():
        raise HTTPException(
            status_code=400,
            detail="VIN should be a 17 characters alpha-numeric string.",
        )
    delete_successful = cache.delete(vin)
    response = {"Input VIN Requested": vin, "Cache Delete Success?": delete_successful}

    return response
