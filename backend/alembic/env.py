# backend/alembic/env.py

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / '.env')


# Backend projenizin ana dizinini (yani 'backend' klasörünü) Python yolu (sys.path) üzerine ekleyin.
sys.path.append(str(Path(__file__).resolve().parents[1]))


from database import Base # Base objesi doğrudan database.py'den alınır.

# KRİTİK KISIM: TÜM MODELLERİ BURADA TEK BİR PAKET OLARAK IMPORT EDİN
# Bu, SQLAlchemy'nin tüm tanımlı modelleri ve ilişkileri otomatik olarak keşfetmesini sağlar.
import models # Bu tek import, models/__init__.py üzerinden tüm modelleri yükler.


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Bu, Alembic'in migrasyonları oluştururken izleyeceği SQLAlchemy meta verisidir.
target_metadata = Base.metadata # Tüm modellerin meta verisi Base objesinde toplanır.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()