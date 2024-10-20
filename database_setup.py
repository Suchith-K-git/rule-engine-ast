import pyodbc

# Set up the connection to SQL Server
try:
    with pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-605868F\\SQLEXPRESS;'
        'DATABASE=Python;'
        'Trusted_Connection=yes;'
    ) as connection:
        with connection.cursor() as cursor:
            # Create a table for rules if it doesn't exist
            cursor.execute('''
            IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'rules')
            BEGIN
                CREATE TABLE dbo.rules (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    rule_name VARCHAR(255) NOT NULL,
                    rule_string TEXT NOT NULL
                )
            END
            ''')
            connection.commit()
            print("Table 'rules' is ready.")

except Exception as e:
    print("Error while connecting to the database or creating the table:", e)
