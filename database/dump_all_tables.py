"""
Dump all user tables from the AWS RDS Postgres.

Outputs:
- Prints every row to stdout (table by table)
- Also writes CSV files to ./dumps/<schema>.<table>.csv

Warning: This prints ALL rows. For large tables set MAX_ROWS_PRINT to limit.
  export MAX_ROWS_PRINT=1000
"""

import os
import csv
import psycopg2


HOST = "elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com"
PORT = 5432
DBNAME = "postgres"
USER = "postgres"
PASSWORD = "ghR4BwyqbEM1xhmrCKbM"


def connect():
    return psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER, password=PASSWORD)


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def dump_table(cur, schema: str, table: str, out_dir: str, max_rows_print: int | None) -> None:
    fq = f"{schema}.{table}"
    print("\n" + "=" * 80)
    print(f"TABLE: {fq}")
    print("=" * 80)

    cur.execute(f"SELECT * FROM {schema}.{table}")
    cols = [d.name for d in cur.description]

    # Write CSV
    ensure_dir(out_dir)
    csv_path = os.path.join(out_dir, f"{schema}.{table}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        printed = 0
        # Stream rows in chunks
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            writer.writerows(rows)
            # Print to stdout (respect optional cap)
            for row in rows:
                if max_rows_print is None or printed < max_rows_print:
                    if printed == 0:
                        print(" | ".join(cols))
                        print("-" * 80)
                    print(" | ".join([str(v) if v is not None else "NULL" for v in row]))
                    printed += 1

    print(f"Saved CSV: {csv_path}")


def main():
    max_rows_print_env = os.environ.get("MAX_ROWS_PRINT", "").strip()
    max_rows_print = None
    if max_rows_print_env:
        try:
            max_rows_print = int(max_rows_print_env)
        except Exception:
            max_rows_print = None

    out_dir = os.path.join(os.path.dirname(__file__), "dumps")

    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type='BASE TABLE'
              AND table_schema NOT IN ('pg_catalog','information_schema')
            ORDER BY table_schema, table_name
            """
        )
        tables = cur.fetchall()

        if not tables:
            print("No user tables found.")
            return

        print(f"Found {len(tables)} tables. Dumping...")
        for schema, table in tables:
            dump_table(cur, schema, table, out_dir, max_rows_print)

        print("\nDone.")


if __name__ == "__main__":
    main()


