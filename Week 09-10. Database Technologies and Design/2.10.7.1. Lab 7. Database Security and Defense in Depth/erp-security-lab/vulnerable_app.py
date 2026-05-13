import psycopg2

# We connect using our RESTRICTED user, not the superuser!
conn = psycopg2.connect("dbname=postgres user=erp_app_user password=app_password123 host=sec-db")
cursor = conn.cursor()

def search_employee_bad(search_term):
    print(f"\n--- VULNERABLE SEARCH for: {search_term} ---")
    # THE FLAW: Using f-strings to build SQL queries allows hackers to inject their own commands
    query = f"SELECT name FROM employees WHERE name = '{search_term}'"
    try:
        cursor.execute(query)
        print(cursor.fetchall())
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

def search_employee_good(search_term):
    print(f"\n--- SECURE SEARCH for: {search_term} ---")
    # THE FIX: Parameterized queries. The database driver sanitizes the input automatically.
    query = "SELECT name FROM employees WHERE name = %s"
    try:
        cursor.execute(query, (search_term,))
        print(cursor.fetchall())
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

# 1. Normal Usage
search_employee_bad("Juan Perez")

# 2. The Attack: The user types a malicious string into the search box
malicious_input = "Juan Perez'; DROP TABLE employees; --"

# Watch the vulnerability in action
search_employee_bad(malicious_input)

# Watch the secure version protect the database
search_employee_good(malicious_input)


# Let's check the Audit Log to see what happened (Requires superuser)
conn_admin = psycopg2.connect("dbname=postgres user=postgres password=superadmin host=sec-db")
admin_cursor = conn_admin.cursor()
admin_cursor.execute("SELECT * FROM audit_log;")
print("\n--- AUDIT LOG ---")
for row in admin_cursor.fetchall():
    print(row)
