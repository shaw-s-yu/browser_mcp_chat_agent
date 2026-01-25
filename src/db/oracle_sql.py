import cx_Oracle
import os

# Initialize Oracle Client - handle different environments
def init_oracle():
    try:
        # Try to initialize with default system paths first
        oracle_home = os.environ.get('ORACLE_HOME')
        if oracle_home:
            lib_dir = os.path.join(oracle_home, 'bin')
            if os.path.exists(lib_dir):
                cx_Oracle.init_oracle_client(lib_dir=lib_dir)
        else:
            # Try common Oracle client paths
            common_paths = [
                r"C:\oracle\instantclient_21_12",
                r"C:\oracle\instantclient_19_20",
                r"C:\app\oracle\product\21c\client_1\bin",
                r"C:\app\db_home\bin"
            ]
            for path in common_paths:
                if os.path.exists(path):
                    cx_Oracle.init_oracle_client(lib_dir=path)
                    break
    except Exception as e:
        print(f"Warning: Could not initialize Oracle Client: {e}")
        # Continue anyway - cx_Oracle might still work with system paths

def lock_timesheet():
     print("Timesheet locked!")

def get_fyppwk(connection, current_date):
    cursor = connection.cursor()
    fiscal_year = cursor.var(cx_Oracle.STRING)
    pay_period = cursor.var(cx_Oracle.STRING)
    pay_week_nbr = cursor.var(cx_Oracle.STRING)
    cursor.callproc("ADMIN.DATECALCULATION.Get_FYPPWK", [current_date, fiscal_year, pay_period, pay_week_nbr])
    cursor.close()
    return fiscal_year.getvalue(), pay_period.getvalue(), pay_week_nbr.getvalue()

if __name__ == "__main__":
    try:
        init_oracle()
        
        # Connection parameters
        host = '10.40.64.105'
        port = 1521
        service_name = 'GSDTIME3'
        user = 'ssyu'
        password = 'itest'
        
        # Create connection
        dsn_tns = cx_Oracle.makedsn(host, port, service_name=service_name)
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
        
        # Test the connection
        fy, pp, pw = get_fyppwk(connection, '06-15-2024')
        print(f"Fiscal Year: {fy}, Pay Period: {pp}, Pay Week Number: {pw}")
        
        connection.close()
    except cx_Oracle.DatabaseError as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")