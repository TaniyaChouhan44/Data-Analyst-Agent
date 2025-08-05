import subprocess
import tempfile

def run_code(code: str):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp.flush()
        try:
            result = subprocess.run(
                ["python", tmp.name],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
