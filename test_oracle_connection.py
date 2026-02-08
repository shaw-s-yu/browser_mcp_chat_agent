#!/usr/bin/env python3
"""
Test script to verify Oracle database connection from Docker container.
Run this script to diagnose Oracle connectivity issues.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_environment():
    """Check if required environment variables are set."""
    print_section("1. Checking Environment Variables")
    
    required_vars = [
        'ORACLE_HOST',
        'ORACLE_PORT',
        'ORACLE_SERVICE',
        'ORACLE_USER',
        'ORACLE_PASSWORD'
    ]
    
    all_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask password
            display_value = '***' if var == 'ORACLE_PASSWORD' else value
            print(f"  ✓ {var}: {display_value}")
        else:
            print(f"  ✗ {var}: NOT SET")
            all_set = False
    
    return all_set

def check_oracle_client():
    """Check if Oracle client is installed."""
    print_section("2. Checking Oracle Client Installation")
    
    try:
        import cx_Oracle
        print(f"  ✓ cx_Oracle module found (version {cx_Oracle.__version__})")
        
        oracle_home = os.environ.get('ORACLE_HOME')
        ld_lib_path = os.environ.get('LD_LIBRARY_PATH', '')
        
        print(f"  ✓ ORACLE_HOME: {oracle_home}")
        print(f"  ✓ LD_LIBRARY_PATH: {ld_lib_path}")
        
        return True
    except ImportError:
        print("  ✗ cx_Oracle module not found!")
        print("    Please install it: pip install cx-Oracle")
        return False
    except Exception as e:
        print(f"  ✗ Error checking Oracle client: {e}")
        return False

def test_connection():
    """Test actual connection to Oracle database."""
    print_section("3. Testing Oracle Database Connection")
    
    try:
        from db.oracle_sql import OracleSQL
        
        print("  Attempting to connect...")
        oracle = OracleSQL()
        connection = oracle.connect()
        
        if connection:
            print("  ✓ Connection successful!")
            
            # Try to execute a simple query
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                cursor.close()
                print("  ✓ Simple query executed: SELECT 1 FROM DUAL")
                print(f"  ✓ Result: {result}")
            except Exception as e:
                print(f"  ⚠ Query execution warning: {e}")
            
            oracle.disconnect()
            return True
        else:
            print("  ✗ Connection failed!")
            return False
            
    except Exception as e:
        print(f"  ✗ Connection error: {e}")
        print(f"\n  Error details: {type(e).__name__}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Oracle Database Connection Test")
    print("="*60)
    
    results = []
    
    # Check environment
    env_ok = check_environment()
    results.append(("Environment Variables", env_ok))
    
    if not env_ok:
        print("\n⚠ WARNING: Some environment variables are not set!")
        print("  Please configure your .env file and ensure it's loaded.")
    
    # Check Oracle client
    client_ok = check_oracle_client()
    results.append(("Oracle Client", client_ok))
    
    # Test connection
    if client_ok:
        conn_ok = test_connection()
        results.append(("Database Connection", conn_ok))
    else:
        results.append(("Database Connection", False))
    
    # Summary
    print_section("Test Summary")
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("  🎉 All tests passed! Oracle connection is working correctly.")
        return 0
    else:
        print("  ❌ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
