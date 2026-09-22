# component: native-path-spelling
# implements: ADR-0031
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: representation only; no I/O, resolution, root selection or authorization
# last_intent_review: 2026-09-21
"""Recognize same-location filesystem spellings; callers retain all path policy."""
from __future__ import annotations

import os
from pathlib import Path, PurePath, PureWindowsPath
import re

__all__ = ("path_identity", "native_io_path")


def path_identity(path: PurePath) -> tuple[str, ...]:
    """Compare filesystem spellings without changing the paths used for I/O."""
    identity = path
    if isinstance(path, PureWindowsPath):
        text = str(path)
        if text.startswith("\\\\?\\"):
            suffix = text[4:]
            if suffix[:4].lower() == "unc\\":
                text = "\\\\" + suffix[4:]
            elif re.match(r"^[A-Za-z]:\\", suffix):
                text = suffix
            else:
                raise ValueError("unsupported Windows filesystem namespace")
        identity = PureWindowsPath(text)
        components = identity.parts[1:]
        if identity.drive.startswith("\\\\"):
            share = identity.drive[2:].split("\\")
            if len(share) != 2:
                raise ValueError("runtime UNC identity requires a server and share")
            components = (*share, *components)
        elif not re.fullmatch(r"[A-Za-z]:", identity.drive):
            raise ValueError("runtime identity requires an absolute filesystem drive")
        if any(
            part in ("", ".", "..") or part.endswith((".", " "))
            or re.search(r'[\x00-\x1f<>:"|?*]', part)
            or PureWindowsPath(part).is_reserved()
            for part in components
        ):
            raise ValueError("ambiguous or non-filesystem Windows path component")
    if not identity.is_absolute() or ".." in identity.parts:
        raise ValueError("runtime identity must be absolute and traversal-free")
    return identity.parts


def native_io_path(path: Path) -> Path:
    """Use only a recognized same-location spelling; never store this I/O alias."""
    if os.name != "nt":
        return path
    path_identity(path)
    text = str(path)
    if text.startswith("\\\\?\\"):
        return path
    return Path("\\\\?\\UNC\\" + text[2:]) if path.drive.startswith("\\\\") else Path("\\\\?\\" + text)
