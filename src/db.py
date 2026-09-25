"""
Database access for the QLFS pipeline: builds a SQLAlchemy engine for the
Postgres warehouse and runs the .sql files under sql/ against it.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine, text

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def get_connection_url():
    """
    Builds a Postgres connection URL from environment variables, with
    defaults that match docker-compose.yml so local runs work out of the
    box.
    """
    user = os.environ.get("POSTGRES_USER", "qlfs")
    password = os.environ.get("POSTGRES_PASSWORD", "qlfs")
    host = os.environ.get("POSTGRES_HOST", "postgres")
    port = os.environ.get("POSTGRES_PORT", "5432")
    database = os.environ.get("POSTGRES_DB", "qlfs")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def get_engine(url=None):
    """
    Returns a SQLAlchemy engine. Pass an explicit `url` (e.g. an in-memory
    SQLite or DuckDB URL) to run against something other than the
    configured Postgres instance, which is what the tests do.
    """
    return create_engine(url or get_connection_url())


def _strip_line_comments(sql_text):
    """
    Removes `-- ...` line comments before statement splitting. Needed
    because a semicolon inside a comment (e.g. "-- a; b") would otherwise
    be mistaken for a statement terminator by the naive split below.
    """
    lines = []
    for line in sql_text.splitlines():
        comment_start = line.find("--")
        lines.append(line if comment_start == -1 else line[:comment_start])
    return "\n".join(lines)


def split_sql_statements(sql_text):
    """
    Splits a .sql file's contents on statement-terminating semicolons.

    This is intentionally simple (it does not understand semicolons
    inside string literals or dollar-quoted bodies, only `--` line
    comments) because every statement in sql/ is a plain CREATE/INSERT/
    SELECT with no such content; a real multi-statement stored procedure
    would need a proper SQL parser instead.
    """
    sql_text = _strip_line_comments(sql_text)
    statements = [s.strip() for s in sql_text.split(";")]
    return [s for s in statements if s]


def run_sql_file(engine, path):
    """
    Executes every statement in a .sql file against `engine`, inside a
    single transaction.
    """
    sql_text = Path(path).read_text()
    statements = split_sql_statements(sql_text)

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def run_sql_dir(engine, directory):
    """
    Runs every .sql file in `directory`, in filename order (hence the
    numeric prefixes on the schema files), so dependent objects are
    always created after the objects they depend on.
    """
    directory = Path(directory)
    sql_files = sorted(directory.glob("*.sql"))

    for sql_file in sql_files:
        run_sql_file(engine, sql_file)


def load_dataframe(df, table_name, engine, schema=None, if_exists="replace"):
    """
    Loads a DataFrame into a SQL table via pandas' to_sql, used to land
    the transformed QLFS data into the staging table.
    """
    df.to_sql(
        table_name,
        engine,
        schema=schema,
        if_exists=if_exists,
        index=False,
    )
