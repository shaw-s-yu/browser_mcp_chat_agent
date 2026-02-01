import cx_Oracle
import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class OracleSQL:
    """Class to handle Oracle database queries and CSV export."""
    
    def __init__(self):
        """Initialize OracleSQL instance."""
        self.connection = None
        self.init_oracle()
    
    def init_oracle(self):
        """Initialize Oracle Client - handle different environments."""
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
    
    def connect(self):
        """Create connection to Oracle database."""
        try:
            host = os.environ.get('ORACLE_HOST')
            port = int(os.environ.get('ORACLE_PORT'))
            service_name = os.environ.get('ORACLE_SERVICE')
            user = os.environ.get('ORACLE_USER')
            password = os.environ.get('ORACLE_PASSWORD')
            
            print("Connecting to Oracle database...")
            dsn_tns = cx_Oracle.makedsn(host, port, service_name=service_name)
            self.connection = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            print("✓ Connected successfully\n")
            return self.connection
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Disconnected")
    
    def execute_query_to_csv(self, sql_query, output_file=None):
        """
        Execute a SQL query and output results to CSV file.
        
        Args:
            sql_query: SQL query string to execute
            output_file: Optional output filename. If not provided, generates timestamp-based name
        
        Returns:
            Path to the generated CSV file
        """
        if not self.connection:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Generate output filename if not provided
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"query_result_{timestamp}.csv"
            
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Write results to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(columns)
                
                # Write data rows
                row_count = 0
                for row in cursor:
                    writer.writerow(row)
                    row_count += 1
            
            cursor.close()
            
            print(f"✓ Query executed successfully")
            print(f"✓ {row_count} rows exported")
            print(f"✓ CSV file saved: {output_file}")
            
            return output_file
        
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    def execute_query_file_to_csv(self, query_file, output_file=None):
        """
        Execute a SQL query from a file and output results to CSV.
        
        Args:
            query_file: Name of the query file in the 'query' folder
            output_file: Optional output filename. If not provided, generates timestamp-based name
        
        Returns:
            Path to the generated CSV file
        """
        # Construct path to query file in query folder
        queries_dir = os.path.join(os.path.dirname(__file__), 'query')
        query_path = os.path.join(queries_dir, query_file)
        
        # Read the SQL query from file
        if not os.path.exists(query_path):
            raise FileNotFoundError(f"Query file not found: {query_path}")
        
        with open(query_path, 'r', encoding='utf-8') as f:
            sql_query = f.read().strip()
        
        if not sql_query:
            raise ValueError("Query file is empty")
        
        # If no output file specified, use default data directory
        if not output_file:
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            output_file = os.path.join(data_dir, 'temp_sql_result.csv')
        
        return self.execute_query_to_csv(sql_query, output_file)
    
    def run_query_file(self, query_file, output_file=None):
        """
        Complete workflow: connect, execute query file, disconnect, and return status message.
        
        Args:
            query_file: Name of the query file in the 'query' folder
            output_file: Optional output filename. If not provided, generates timestamp-based name
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.connect()
            result_file = self.execute_query_file_to_csv(query_file, output_file)
            self.disconnect()
            return (True, f"Success: Query results saved to {result_file}")
        except FileNotFoundError as e:
            return (False, f"Error: {str(e)}")
        except ValueError as e:
            return (False, f"Error: {str(e)}")
        except cx_Oracle.DatabaseError as e:
            return (False, f"Database Error: {str(e)}")
        except Exception as e:
            return (False, f"Error: {str(e)}")


def main():
    """Main CLI function for backward compatibility."""
    if len(sys.argv) < 2:
        print("Usage: python oracle_sql.py '<QUERY_FILE>'")
        print("\nExample:")
        print("  python oracle_sql.py 'my_query.sql'")
        print("\nThe query file should be located in the 'query' folder")
        sys.exit(1)
    
    query_file = sys.argv[1]
    
    oracle = OracleSQL()
    success, message = oracle.run_query_file(query_file)
    print(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()