# Integration Tests

This directory contains blackbox integration tests for the Teams bot application using the testcontainers framework.

## Overview

The integration tests are true blackbox tests that:
- Run the application in a Docker container
- Make real HTTP requests to the containerized application
- Test both endpoints: `GET /api/messages` and `POST /api/messages`
- Validate card output structure against ChannelAPI-OpenAPI.yaml schema

## Prerequisites

1. **Docker**: Make sure Docker is installed and running on your machine
   ```bash
   docker --version
   ```

2. **Python Dependencies**: Install test dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Running the Tests

Run all integration tests:
```bash
pytest tests/test_integration.py -v
```

Run a specific test:
```bash
pytest tests/test_integration.py::test_get_messages_health_check -v
```

Run with verbose output:
```bash
pytest tests/test_integration.py -v -s
```

## Test Structure

The tests use testcontainers to:
1. Build a Docker image of the application
2. Start a container with the application
3. Wait for the server to be ready
4. Execute tests against the running container
5. Clean up the container after tests complete

## Test Coverage

The integration tests cover:

- ✅ `GET /api/messages` - Health check endpoint
- ✅ `POST /api/messages` - Direct message handling
- ✅ `POST /api/messages` - Channel message handling
- ✅ Empty message filtering
- ✅ Card structure validation (HeroCard schema compliance)
- ✅ Conversation update handling
- ✅ Error handling for invalid activities

## Environment Variables

The tests automatically set the following environment variables in the container:
- `TARGET_USER_ID=test-user-123`
- `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=test-client-id`
- `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=test-secret`
- `CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=test-tenant-id`
- `PORT=3978`

## Troubleshooting

### Container fails to start
- Ensure Docker is running: `docker ps`
- Check Docker logs: `docker logs <container-id>`
- Verify the Dockerfile builds successfully

### Port conflicts
- The tests use port 3978 by default
- If the port is in use, you may need to stop other services using that port

### Timeout errors
- Increase the retry count in the test fixture if your machine is slow
- Check that the application starts correctly in the container

## Notes

- Tests are module-scoped, meaning the container is started once for all tests in the module
- The Docker image is built fresh for each test run
- The container is automatically cleaned up after tests complete
