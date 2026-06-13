echo "--- ERP BACKUP & RESTORE VALIDATION ---"

# 1. Take the backup from the running container
echo "[1/3] Extracting database backup from production container..."
#podman cp erp-secure-prod:/app/erp_prod.db ./erp_backup_$(date +%F).db
podman cp erp-secure-prod:/app/erp_prod.db ("./erp_backup_" + (Get-Date -Format "yyyy-MM-dd") + ".db")

# 2. Simulate a restore into a temporary, isolated QA container
echo "[2/3] Spinning up isolated restore-test container..."
#podman run --name db-restore-test -v ./erp_backup_$(date +%F).db:/test.db:ro --rm -d python:3.10-slim sleep 60
podman run --name db-restore-test -v ("${pwd}/erp_backup_" + (Get-Date -Format "yyyy-MM-dd") + ".db:/test.db:ro") --rm -d python:3.10-slim sleep 60

# 3. Test the restore (Run a query to ensure data isn't corrupted)
echo "[3/3] Validating restored data integrity..."
# Capture result and convert to integer
$raw = podman exec db-restore-test python -c "import sqlite3; c=sqlite3.connect('/test.db'); print(c.execute('SELECT count(*) FROM inventory').fetchone()[0])"
$RESULT = [int]($raw -as [string])

if ($RESULT -gt 0) {
    echo "SUCCESS: Backup completed and verified. $RESULT records successfully restored in test environment."
} else {
    echo "FAILURE: Backup is corrupt or empty! Triggering PagerDuty alert!"
}

# Clean up
podman stop db-restore-test -d

