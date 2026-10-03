import subprocess
import sys
import sqlite3
from datetime import datetime


DB_PATH = r"..\database\ecommerce.db"


# --------------------------------------------------
# 1. Check source file argument
# --------------------------------------------------

if len(sys.argv) < 2:
    print("Error: Source file not provided.")
    print("Usage: python pipeline.py <source_file>")
    sys.exit(1)

source_file = sys.argv[1]


# --------------------------------------------------
# 2. Create pipeline run record
# --------------------------------------------------

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

run_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cursor.execute("""
    INSERT INTO pipeline_runs (
        pipeline_name,
        run_start_time,
        status
    )
    VALUES (?, ?, ?)
""", (
    "orders_pipeline",
    run_start,
    "RUNNING"
))

run_id = cursor.lastrowid

conn.commit()
conn.close()

print(f"Pipeline Run ID: {run_id}")
print(f"Source file: {source_file}")


# --------------------------------------------------
# 3. Pipeline steps
# --------------------------------------------------

steps = [
    ["incremental_extract.py", source_file],
    ["stage_incremental.py", source_file],
    ["validate_incremental.py"],
    ["save_rejected.py"],
    ["upsert_orders.py", str(run_id)],
    ["update_watermark.py"]
]


# --------------------------------------------------
# 4. Execute pipeline
# --------------------------------------------------

success = True

for step in steps:

    script = step[0]

    print(f"\nRunning: {script}")
    print("-" * 50)

    result = subprocess.run(
        [sys.executable] + step
    )

    if result.returncode != 0:

        success = False

        print(f"\nPipeline failed at: {script}")

        break


# --------------------------------------------------
# 5. Cleanup staging only after success
# --------------------------------------------------

if success:

    print("\nRunning: cleanup_staging.py")
    print("-" * 50)

    cleanup_result = subprocess.run(
        [sys.executable, "cleanup_staging.py"]
    )

    if cleanup_result.returncode != 0:

        success = False

        print("\nPipeline failed during staging cleanup.")


# --------------------------------------------------
# 6. Read actual counts from database
# --------------------------------------------------

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# Extracted

cursor.execute("""
    SELECT COUNT(*)
    FROM orders_staging
""")

records_extracted = cursor.fetchone()[0]


# Rejected

cursor.execute("""
    SELECT COUNT(*)
    FROM rejected_orders
    WHERE rejected_at >= ?
""", (run_start,))

records_rejected = cursor.fetchone()[0]


# Valid

records_valid = records_extracted - records_rejected


# Inserted / Updated

cursor.execute("""
    SELECT
        records_inserted,
        records_updated
    FROM pipeline_run_counts
    WHERE run_id = ?
""", (run_id,))

count_result = cursor.fetchone()

if count_result:
    records_inserted = count_result[0]
    records_updated = count_result[1]
else:
    records_inserted = 0
    records_updated = 0


# --------------------------------------------------
# 7. Read current watermark
# --------------------------------------------------

cursor.execute("""
    SELECT last_successful_watermark
    FROM pipeline_control
    WHERE pipeline_name = 'orders_pipeline'
""")

watermark = cursor.fetchone()[0]


# --------------------------------------------------
# 8. Update pipeline run
# --------------------------------------------------

run_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

status = "SUCCESS" if success else "FAILED"

cursor.execute("""
    UPDATE pipeline_runs
    SET
        run_end_time = ?,
        status = ?,
        records_extracted = ?,
        records_valid = ?,
        records_rejected = ?,
        records_inserted = ?,
        records_updated = ?,
        watermark = ?
    WHERE run_id = ?
""", (
    run_end,
    status,
    records_extracted,
    records_valid,
    records_rejected,
    records_inserted,
    records_updated,
    watermark,
    run_id
))

conn.commit()


# --------------------------------------------------
# 9. Display run log
# --------------------------------------------------

cursor.execute("""
    SELECT *
    FROM pipeline_runs
    WHERE run_id = ?
""", (run_id,))

print("\nPipeline Run Log:")
print(cursor.fetchone())

conn.close()


# --------------------------------------------------
# 10. Final result
# --------------------------------------------------

if not success:

    print("\n" + "=" * 50)
    print("PIPELINE FAILED")
    print("=" * 50)

    sys.exit(1)


print("\n" + "=" * 50)
print("PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 50)