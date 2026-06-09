from app.models import Base


def test_models_registered():
    """
    Verifies that all required ORM models are registered in SQLAlchemy's metadata.
    Ensures no syntax errors, structural defects, or circular reference issues exist.
    """
    tables = Base.metadata.tables
    
    expected_tables = {
        "companies",
        "users",
        "vendors",
        "invoices",
        "workflows",
        "reports",
        "agent_runs",
        "chat_history",
        "analytics",
    }
    
    for table_name in expected_tables:
        assert table_name in tables, f"Model table '{table_name}' was not found in metadata"
