from sqlalchemy import create_engine, text

# Your connection string
DB_URL = "postgresql+psycopg2://postgres:1203@localhost/stock_app"

engine = create_engine(DB_URL)

def execute(query, params=None, fetchall=False, fetchone=False):
    with engine.connect() as conn:
        # We use text(query) to ensure SQLAlchemy handles the SQL correctly
        result = conn.execute(text(query), params or {})
        
        if fetchall:
            return result.fetchall()
        if fetchone:
            return result.fetchone()
        
        conn.commit()
    return None