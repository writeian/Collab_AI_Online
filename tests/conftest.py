"""Pytest-wide setup.

Isolate the test run from any real/dev database *before* the application is
imported anywhere. Importing the app binds SQLAlchemy to whatever DATABASE_URL
is set (defaulting to instance/ai_collab.db), and some tests call
``db.drop_all()`` — without this, running the suite would wipe the developer's
local database. conftest.py is imported by pytest before any test module, so
setting the URL here guarantees every test uses a throwaway file DB instead.
"""

import os
import tempfile

# A dedicated temp file (not sqlite :memory:, which gives each pooled connection
# its own private database and breaks tests that use more than one connection).
_TEST_DB = os.path.join(tempfile.gettempdir(), "collab_ai_test.db")
os.environ["DATABASE_URL"] = "sqlite:///" + _TEST_DB
