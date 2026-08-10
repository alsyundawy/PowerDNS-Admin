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
if config.config_file_name:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from flask import current_app
db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI') or ''
config.set_main_option('sqlalchemy.url', db_uri.replace("%", "%%"))
target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

import sqlalchemy as sa
from alembic.operations import Operations
from alembic.operations.batch import ApplyBatchImpl
from alembic.ddl.impl import DefaultImpl

_orig_impl_exec = DefaultImpl._exec
_orig_batch_drop_column = ApplyBatchImpl.drop_column


def _safe_impl_exec(self, construct, execution_options=None, multiparams=None, params=None):
    try:
        return _orig_impl_exec(self, construct, execution_options=execution_options, multiparams=multiparams, params=params)
    except Exception as ex:
        err_msg = str(ex).lower()
        if any(ign in err_msg for ign in ["already exists", "duplicate", "no such column"]):
            logger.info("Ignoring safe DDL error: %s", ex)
            return
        raise


def _safe_batch_drop_column(self, column, *args, **kwargs):
    col_name = getattr(column, 'name', column)
    if col_name not in self.columns:
        logger.info("Column '%s' not present in batch columns, skipping batch drop_column.", col_name)
        return
    return _orig_batch_drop_column(self, column, *args, **kwargs)


DefaultImpl._exec = _safe_impl_exec
ApplyBatchImpl.drop_column = _safe_batch_drop_column


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

    section = config.get_section(config.config_ini_section) or {}
    engine = engine_from_config(section,
                                prefix='sqlalchemy.',
                                poolclass=pool.NullPool)

    connection = engine.connect()
    configure_opts = current_app.extensions['migrate'].configure_args.copy()
    if 'render_as_batch' not in configure_opts:
        sql_url = config.get_main_option('sqlalchemy.url') or ''
        configure_opts['render_as_batch'] = sql_url.startswith('sqlite:')

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
