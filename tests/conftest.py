"""Shared helpers. Works in both layouts: the published repo (scripts in tools/, site at the root)
and the local working folder (scripts at the root, site in web/)."""
import importlib.util
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools" if (ROOT / "tools" / "build_pages.py").exists() else ROOT
SITE = ROOT if (ROOT / "index.html").exists() else ROOT / "web"
AREAS = TOOLS / "areas.geojson" if (TOOLS / "areas.geojson").exists() else ROOT / "data" / "areas.geojson"


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def site():
    return SITE
