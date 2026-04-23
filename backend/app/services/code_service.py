import httpx, tempfile, os, asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings

async def execute_code(language: str, source_code: str, stdin: str = "", version: str = "*") -> Dict[str, Any]:
    payload = {"language": language, "version": version,
                "files": [{"name": "main", "content": source_code}],
                "stdin": stdin, "args": [],
                "compile_timeout": 10000, "run_timeout": 5000}
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.post(f"{settings.PISTON_API_URL}/execute", json=payload)
            if r.status_code == 200:
                return r.json()
            print(f"[PISTON] {r.status_code} - local fallback")
    except Exception as e:
        print(f"[PISTON] {e} - local fallback")
    if language in ("python", "python3"):
        return await _run_local(source_code, stdin)
    return {"run": {"stdout": "", "stderr": f"No executor for {language}", "code": 1}}

async def run_test_cases(language: str, source_code: str, test_cases: List[Dict[str, Any]], wrapper: Optional[str] = None) -> List[Dict[str, Any]]:
    nl = chr(10)
    full = source_code + (nl+nl + wrapper if wrapper else "")
    results = []
    for i, tc in enumerate(test_cases):
        try:
            res = await execute_code(language, full, stdin=tc.get("input", ""))
            ro = res.get("run", {})
            actual = ro.get("stdout", "").strip()
            expected = tc.get("expected_output", "").strip()
            results.append({"test_case_index": i, "passed": actual == expected,
                            "actual_output": actual,
                            "expected_output": expected if not tc.get("is_hidden") else "***",
                            "stderr": ro.get("stderr", ""), "is_hidden": tc.get("is_hidden", False)})
        except Exception as e:
            results.append({"test_case_index": i, "passed": False, "error": str(e), "is_hidden": tc.get("is_hidden", False)})
    return results

async def get_available_runtimes() -> List[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(f"{settings.PISTON_API_URL}/runtimes")
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return [{"language": "python", "version": "3.11.0"}]

async def _run_local(source_code: str, stdin: str = "") -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
        f.write(source_code)
        tmp = f.name
    try:
        proc = await asyncio.create_subprocess_exec(
            "python3", tmp, stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await asyncio.wait_for(proc.communicate(stdin.encode()), timeout=settings.LOCAL_EXEC_TIMEOUT)
        return {"run": {"stdout": out.decode(), "stderr": err.decode(), "code": proc.returncode}}
    except asyncio.TimeoutError:
        return {"run": {"stdout": "", "stderr": "Timed out", "code": 1}}
    except Exception as e:
        return {"run": {"stdout": "", "stderr": str(e), "code": 1}}
    finally:
        if os.path.exists(tmp): os.remove(tmp)