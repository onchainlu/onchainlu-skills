"""Shared page rasterizer with a fallback chain: pypdfium2 -> pdftoppm.

Returns PIL Images so callers can annotate/save. Not a CLI.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

PDFTOPPM_TIMEOUT_SECONDS = 30


class RasterError(RuntimeError):
    """Safe, structured rasterizer failure suitable for CLI JSON output."""

    def __init__(self, code: str, backend: str, page: int, message: str):
        super().__init__(message)
        self.code = code
        self.backend = backend
        self.page = page
        self.message = message

    def as_dict(self) -> dict:
        return {"code": self.code, "backend": self.backend,
                "page": self.page, "message": self.message}


def available_backends() -> list[str]:
    """Names of usable rasterizer backends, in preference order."""
    backends = []
    try:
        import pypdfium2  # noqa: F401
        backends.append("pypdfium2")
    except ImportError:
        pass
    if shutil.which("pdftoppm"):
        backends.append("pdftoppm")
    return backends


def missing_hints() -> list[str]:
    """Dependency names for when no backend is available."""
    return [
        "pypdfium2 (preferred)",
        "pdftoppm (from Poppler)",
    ]


def rasterize_page(pdf_path: str, page: int, dpi: int = 150, password: str | None = None):
    """Render one 1-based page to a PIL Image, or None if no backend works."""
    for backend in available_backends():
        if backend == "pypdfium2":
            try:
                return _via_pdfium(pdf_path, page, dpi, password)
            except RasterError:
                raise
            except Exception as exc:
                raise RasterError(
                    "backend_failed", "pypdfium2", page,
                    "pypdfium2 failed to render the requested page",
                ) from exc
        if backend == "pdftoppm":
            img = _via_pdftoppm(pdf_path, page, dpi, password)
            if img is not None:
                return img
    return None


def _via_pdfium(pdf_path: str, page: int, dpi: int, password: str | None):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf_path, password=password)
    try:
        if not 1 <= page <= len(doc):
            raise ValueError(f"page {page} out of range 1-{len(doc)}")
        bitmap = doc[page - 1].render(scale=dpi / 72.0)
        return bitmap.to_pil().convert("RGB")
    finally:
        doc.close()


def _via_pdftoppm(pdf_path: str, page: int, dpi: int, password: str | None):
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        prefix = str(Path(tmp) / "page")
        cmd = ["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page)]
        if password:
            cmd += ["-upw", password]
        cmd += [pdf_path, prefix]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8",
                timeout=PDFTOPPM_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise RasterError(
                "timeout", "pdftoppm", page,
                f"pdftoppm timed out after {PDFTOPPM_TIMEOUT_SECONDS} seconds",
            ) from exc
        if proc.returncode != 0:
            raise RasterError(
                "backend_failed", "pdftoppm", page,
                "pdftoppm failed to render the requested page",
            )
        produced = sorted(Path(tmp).glob("page*.png"))
        if not produced:
            raise RasterError(
                "no_output", "pdftoppm", page,
                "pdftoppm produced no image for the requested page",
            )
        with Image.open(produced[0]) as img:
            return img.convert("RGB")
