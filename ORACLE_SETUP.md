# Oracle Docker Setup - Changes Summary

This document outlines all changes made to support Oracle database connections from within a Docker container.

## Files Modified

### 1. **Dockerfile**
**Changes:**
- Added `libaio1` and `unzip` packages for Oracle Instant Client support
- Added Step 4: Oracle Instant Client 21.4 installation
- Added environment variables: `LD_LIBRARY_PATH` and `ORACLE_HOME`

**Why:**
- `libaio1`: Required dependency for Oracle Instant Client
- `unzip`: Needed to extract Instant Client
- Oracle Instant Client: Allows cx_Oracle to connect to remote Oracle servers
- Environment variables: Tell the system where to find Oracle libraries

### 2. **docker-compose.yml**
**Changes:**
- Added `environment` section with Oracle connection parameters
- Variables include: `ORACLE_HOST`, `ORACLE_PORT`, `ORACLE_SERVICE`, `ORACLE_USER`, `ORACLE_PASSWORD`
- Also sets `LD_LIBRARY_PATH` and `ORACLE_HOME`

**Why:**
- Makes credentials configurable without changing code
- Values are read from `.env` file using `${VAR_NAME}` syntax
- Allows different configurations for dev/prod environments

### 3. **entrypoint.sh**
**Changes:**
- Added export of Oracle environment variables at startup
- Sets `LD_LIBRARY_PATH` and `ORACLE_HOME`

**Why:**
- Ensures Oracle libraries are accessible when scripts run
- Guarantees correct library path priority
- Runs before all other processes in container

### 4. **src/db/oracle_sql.py**
**Changes:**
- Completely rewrote `init_oracle()` method
- Now checks multiple paths including Docker Linux paths
- Better error handling and logging
- Supports Docker, Windows, and Linux environments

**Key improvements:**
```python
# Now checks these paths in order:
'/opt/oracle/instantclient_21_4',      # Docker Linux (primary)
'/opt/oracle/instantclient_19_20',     # Docker Linux (alt)
r"C:\oracle\instantclient_21_12",      # Windows
r"C:\oracle\instantclient_19_20",      # Windows (alt)
r"C:\app\oracle\product\21c\client_1\bin",
r"C:\app\db_home\bin"
```

## Files Created

### 1. **.env.example**
Template file showing all required environment variables:
```
GEMINI_API_KEY=your_gemini_api_key_here
ORACLE_HOST=your_oracle_server_ip
ORACLE_PORT=1521
ORACLE_SERVICE=your_service_name
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
```

**Usage:** Copy to `.env` and fill in your values

### 2. **test_oracle_connection.py**
Diagnostic script to test Oracle connectivity:
```bash
# Usage:
python test_oracle_connection.py
```

**Tests:**
1. Environment variables are set
2. Oracle Instant Client is installed
3. cx_Oracle module is available
4. Actual database connection succeeds
5. Simple SQL query executes

## How It Works

### Installation Flow (in Dockerfile):

1. **Install dependencies:**
   ```dockerfile
   apt-get install libaio1 unzip
   ```

2. **Download Oracle Instant Client 21.4:**
   ```dockerfile
   wget https://download.oracle.com/otn_software/linux/instantclient/214000/instantclient-basic-linux.x64-21.4.0.0.0dbru.zip
   ```

3. **Extract and configure:**
   ```dockerfile
   unzip instantclient-basic-linux.x64-21.4.0.0.0dbru.zip
   ldconfig  # Update library cache
   ```

4. **Set environment variables:**
   ```dockerfile
   ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_4:$LD_LIBRARY_PATH
   ENV ORACLE_HOME=/opt/oracle/instantclient_21_4
   ```

### Connection Flow (at runtime):

1. **Docker container starts**
2. **entrypoint.sh runs** → exports Oracle environment variables
3. **Python app imports** `cx_Oracle` → loads Oracle libraries
4. **OracleSQL.init_oracle()** → finds and initializes Oracle client
5. **OracleSQL.connect()** → uses environment variables to connect to remote server

## Setup Instructions

### For Docker:

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your Oracle credentials
nano .env

# 3. Build and run
docker-compose up -d --build

# 4. Test connection (optional)
docker exec -it ubuntu-novnc python /home/user/app/test_oracle_connection.py
```

### For Local Development (Windows/macOS):

```bash
# 1. Download Oracle Instant Client from:
# https://www.oracle.com/database/technologies/instant-client.html

# 2. Extract to a known location (e.g., C:\oracle\instantclient_21_12)

# 3. Add to PATH or set ORACLE_HOME

# 4. Create .env from example
cp .env.example .env

# 5. Fill in credentials and run
python src/app.py
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "Cannot locate Oracle libraries" | ORACLE_HOME not set | Check Dockerfile env vars |
| "Cannot create connection" | Wrong credentials | Verify .env file |
| "Connection timeout" | Can't reach server | Check firewall, verify ORACLE_HOST |
| "ORA-12505" | Invalid service name | Correct ORACLE_SERVICE value |

## Verification Checklist

- [ ] Dockerfile includes Oracle Instant Client installation
- [ ] docker-compose.yml has environment variables section
- [ ] .env file created and configured with real credentials
- [ ] entrypoint.sh exports Oracle environment variables
- [ ] oracle_sql.py has updated init_oracle() method
- [ ] test_oracle_connection.py script works (optional but recommended)

## Next Steps

1. **Configure credentials:** Update `.env` with your Oracle server details
2. **Build Docker image:** `docker-compose up -d --build`
3. **Test connection:** Run `test_oracle_connection.py` inside container
4. **Create SQL queries:** Add `.sql` files to `src/db/query/`
5. **Create prompts:** Add `.md` files to `src/prompts/`
6. **Register actions:** Update `src/action_mapper.json`
