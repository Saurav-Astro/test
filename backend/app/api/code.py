from fastapi import APIRouter
from app.services.code_service import get_available_runtimes

router = APIRouter(prefix="/code", tags=["Code"])


@router.get("/runtimes")
async def runtimes():
    """Return available language runtimes from Piston."""
    data = await get_available_runtimes()
    # Simplify to {language, version}
    seen = set()
    result = []
    for r in data:
        key = r["language"]
        if key not in seen:
            seen.add(key)
            result.append({"language": r["language"], "version": r["version"]})
    return sorted(result, key=lambda x: x["language"])
