import os
from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None
try:
    from app.models.user import Base
    from app.models.lead import Lead  # noqa: F401
    target_metadata = Base.metadata
except Exception as e:
    print(f'Warning: Could not load metadata: {e}')

def run_migrations_online():
    url = os.getenv("DATABASE_URL", "postgresql://yukti_user:yukti_password_secure@localhost:5432/yukti_db")
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
