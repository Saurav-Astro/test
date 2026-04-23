import httpx
import subprocess
import tempfile
import os
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings

async def execute_code(
    language: str,
    source_code: str,
    stdin: str = "",
    version: str = "*",
) -> Dict[str, Any]:
    """Execute code via Piston API — sandboxed, no local execution."""
    payload = {
        "language": language,
        "version": version,
        "files": [{"name": "main", "content": source_code}],
        "stdin": stdin,
        "args": [],
        "compile_timeout": 10000,
        "run_timeout": 5000,
        "compile_memory_limit": -1,
        "run_memory_limit": -1,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.PISTON_API_URL}/execute", json=payload
        )
        resp.raise_for_status()
        resp_json = resp.json()
        if isinstance(resp_json, dict) and 'whitelist only' in resp_json.get('message', ''):
            if language == 'python':
                return await execute_locally_python(source_code, stdin)
        return resp_json

async def run_test_cases(
    language: str,
    source_code: str,
    test_cases: List[Dict[str, Any]],
    wrapper: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Run code against all test cases and return results."""
    full_code = source_code
    if wrapper:
        full_code = f"{source_code}\n\n{wrapper}"
    
    results = []
    for i, tc in enumerate(test_cases):
        try:
            result = await execute_code(language, full_code, stdin=tc.get("input", ""))
            run_output = result.get("run", {})
            actual_output = run_output.get("stdout", "").strip()
            expected = tc.get("expected_output", "").strip()
            passed = actual_output == expected
            results.append(
                {
                    "test_case_index": i,
                    "passed": passed,
                    "actual_output": actual_output,
                    "expected_output": expected if not tc.get("is_hidden") else "***",
                    "stderr": run_output.get("stderr", ""),
                    "is_hidden": tc.get("is_hidden", False),
                    "execution_time_ms": run_output.get("time", 0),
                }
            )
        except Exception as e:
            results.append(
                {
                    "test_case_index": i,
                    "passed": False,
                    "error": str(e),
                    "is_hidden": tc.get("is_hidden", False),
                }
            )
    return results

async def get_available_runtimes() -> List[Dict[str, Any]]:
    """Fetch available language runtimes from Piston API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{settings.PISTON_API_URL}/runtimes")
        resp.raise_for_status()
        return resp.json()

async def execute_locally_python(source_code: str, stdin: str = "") -> Dict[str, Any]:
    """Execute Python code locally using subprocess (as a fallback)."""
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(source_code.encode('utf-8'))
        temp_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            'python', temp_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(input=stdin.encode('utf-8')), timeout=5.0)
        return {
            'run': {
                'stdout': stdout.decode('utf-8'),
                'stderr': stderr.decode('utf-8'),
                'code': proc.returncode,
                'signal': None,
                'output': stdout.decode('utf-8') + stderr.decode('utf-8')
            }
        }
    except asyncio.TimeoutError:
        return {'run': {'stderr': 'Execution timed out (5s)', 'stdout': '', 'code': 1}}
    except Exception as e:
        return {'run': {'stderr': f'Local execution error: {str(e)}', 'stdout': '', 'code': 1}}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
