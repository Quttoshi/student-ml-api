"""Ensures the repository root (where app.py lives) is on sys.path for tests.

pytest's default "prepend" import mode adds the directory of each test file
to sys.path when that directory has no __init__.py. tests/ intentionally has
no __init__.py, so without this root conftest.py, `from app import app`
inside tests/test_app.py would fail. A conftest.py at the repository root is
always imported by pytest and its own directory is added to sys.path as a
side effect, which is all this file needs to do.
"""
