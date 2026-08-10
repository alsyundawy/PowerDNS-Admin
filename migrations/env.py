from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import logging

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from flask import current_app
config.set_main_option('sqlalchemy.url',
                       current_app.config.get('SQLALCHEMY_DATABASE_URI').replace("%","%%"))
target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    engine = engine_from_config(config.get_section(config.config_ini_section),
                                prefix='sqlalchemy.',
                                poolclass=pool.NullPool)

    connection = engine.connect()
    configure_opts = current_app.extensions['migrate'].configure_args.copy()
    if 'render_as_batch' not in configure_opts:
        sql_url = config.get_main_option('sqlalchemy.url') or ''
        configure_opts['render_as_batch'] = sql_url.startswith('sqlite:')

    import sqlalchemy as sa
    from alembic.script import ScriptDirectory

    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    if 'account' in tables:
        has_version = False
        if 'alembic_version' in tables:
            res = connection.execute(sa.text("SELECT version_num FROM alembic_version")).fetchall()
            if len(res) > 0:
                has_version = True
        if not has_version:
            script = ScriptDirectory.from_config(config)
            head_revision = script.get_current_head()
            if head_revision:
                logger.info("Database tables already exist. Stamping alembic_version to head (%s).", head_revision)
                connection.execute(sa.text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
                connection.execute(sa.text("DELETE FROM alembic_version"))
                connection.execute(sa.text("INSERT INTO alembic_version (version_num) VALUES (:ver)"), {"ver": head_revision})
                if hasattr(connection, 'commit'):
                    connection.commit()
                connection.close()
                return

    context.configure(connection=connection,
                      target_metadata=target_metadata,
                      process_revision_directives=process_revision_directives,
                      **configure_opts)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
