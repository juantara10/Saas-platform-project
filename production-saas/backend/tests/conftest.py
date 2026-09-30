import os
os.environ["DATABASE_URL"]="sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.db import Base, engine
from app.main import app
import pytest
@pytest.fixture(autouse=True)
def clean_db():
 Base.metadata.drop_all(engine); Base.metadata.create_all(engine); yield; Base.metadata.drop_all(engine)
@pytest.fixture
def client(): return TestClient(app)
