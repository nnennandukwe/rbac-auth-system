# RBAC Auth System - Test Suite

This directory contains comprehensive tests for the RBAC (Role-Based Access Control) Authentication System. The test suite covers all aspects of the system including authentication, authorization, database models, and integration scenarios.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_auth.py               # Authentication endpoint tests
├── test_protected_routes.py   # Protected route access tests
├── test_models.py             # Database model tests
├── test_permissions.py        # Permission system tests
├── test_auth_utils.py         # Authentication utility tests
├── test_integration.py        # End-to-end integration tests
└── README.md                  # This file
```

## Test Categories

### 1. Authentication Tests (`test_auth.py`)
- **User Registration**: Tests for user registration with different roles
- **User Login**: Tests for login functionality and token generation
- **Token Validation**: Tests for JWT token validation and security
- **Error Handling**: Tests for various authentication error scenarios

**Key Test Classes:**
- `TestUserRegistration`: Registration with various role combinations
- `TestUserLogin`: Login scenarios for all user types
- `TestTokenValidation`: JWT token security and validation

### 2. Protected Routes Tests (`test_protected_routes.py`)
- **Admin Route Access**: Tests for `/admin` endpoint (requires `can_delete`)
- **Editor Route Access**: Tests for `/edit` endpoint (requires `can_write`)
- **Viewer Route Access**: Tests for `/view` endpoint (requires `can_read`)
- **Role Permission Matrix**: Complete testing of role-permission combinations

**Key Test Classes:**
- `TestAdminRouteAccess`: Admin-only endpoint access
- `TestEditorRouteAccess`: Editor-level endpoint access
- `TestViewerRouteAccess`: Viewer-level endpoint access
- `TestRolePermissionMatrix`: Complete permission matrix validation

### 3. Database Models Tests (`test_models.py`)
- **User Model**: User creation, validation, and relationships
- **Role Model**: Role management and user associations
- **Permission Model**: Permission creation and role assignments
- **Relationships**: Many-to-many relationship testing

**Key Test Classes:**
- `TestUserModel`: User model functionality and validation
- `TestRoleModel`: Role model and user relationships
- `TestPermissionModel`: Permission model and role relationships
- `TestModelRelationships`: Complex relationship scenarios

### 4. Permission System Tests (`test_permissions.py`)
- **Permission Checking**: Core permission validation logic
- **Dependency System**: FastAPI dependency testing
- **Role Combinations**: Multi-role permission scenarios
- **Edge Cases**: Permission system edge cases and security

**Key Test Classes:**
- `TestCheckUserPermission`: Core permission checking function
- `TestRequirePermissionDependency`: FastAPI permission dependencies
- `TestPermissionScenarios`: Various permission scenarios

### 5. Authentication Utilities Tests (`test_auth_utils.py`)
- **Password Hashing**: Bcrypt password hashing and verification
- **JWT Tokens**: Token creation, validation, and security
- **User Retrieval**: Current user extraction from tokens
- **Security Properties**: Authentication security features

**Key Test Classes:**
- `TestPasswordHashing`: Password security and hashing
- `TestJWTTokens`: JWT token functionality
- `TestGetCurrentUser`: User retrieval from tokens
- `TestAuthUtilsIntegration`: Integration between auth components

### 6. Integration Tests (`test_integration.py`)
- **Complete Workflows**: End-to-end user workflows
- **Security Scenarios**: Security testing and attack prevention
- **Error Handling**: System-wide error handling
- **Concurrent Access**: Multi-user concurrent access testing

**Key Test Classes:**
- `TestCompleteUserWorkflow`: Full user journey testing
- `TestSecurityScenarios`: Security and attack prevention
- `TestErrorHandling`: Error scenarios and recovery
- `TestConcurrentAccess`: Multi-user system testing

## Test Coverage

The test suite provides comprehensive coverage for:

### ✅ **Authentication & Authorization**
- User registration with all role types (Admin, Editor, Viewer)
- Multi-role user registration and management
- Login functionality for all user types
- JWT token creation, validation, and expiration
- Password hashing and verification security
- Permission-based access control

### ✅ **Role-Based Access Control**
- **Admin Role**: Full access (can_read, can_write, can_delete)
- **Editor Role**: Read and write access (can_read, can_write)
- **Viewer Role**: Read-only access (can_read)
- **Multi-Role Users**: Combined permissions from multiple roles
- **No-Role Users**: Proper access denial

### ✅ **Database Models**
- User model creation and validation
- Role and permission model functionality
- Many-to-many relationships (User-Role, Role-Permission)
- Database constraints and integrity
- Model method functionality (`has_permission`, etc.)

### ✅ **Security Features**
- Password hashing with bcrypt and salt
- JWT token security and expiration
- Permission escalation prevention
- Token reuse prevention
- Input validation and sanitization

### ✅ **Error Handling**
- Duplicate registration prevention
- Invalid login handling
- Token validation errors
- Permission denial responses
- Database constraint violations

### ✅ **Integration Scenarios**
- Complete user workflows from registration to resource access
- Multi-user concurrent access
- Cross-role permission testing
- System-wide error recovery

## Running Tests

### Prerequisites
```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio httpx

# Optional: Install coverage and parallel execution
pip install pytest-cov pytest-xdist
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestUserRegistration

# Run specific test method
pytest tests/test_auth.py::TestUserRegistration::test_register_user_with_viewer_role
```

### Using the Test Runner Script

```bash
# Make the script executable (if needed)
chmod +x run_tests.py

# Run all tests
python run_tests.py

# Run specific test suites
python run_tests.py --suite unit
python run_tests.py --suite integration
python run_tests.py --suite auth
python run_tests.py --suite permissions
python run_tests.py --suite models

# Run with coverage
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose

# Run tests in parallel
python run_tests.py --parallel 4

# Stop on first failure
python run_tests.py --failfast
```

### Test Suite Options

| Suite | Description | Files Included |
|-------|-------------|----------------|
| `all` | All tests (default) | All test files |
| `unit` | Unit tests only | Models, permissions, auth utils |
| `integration` | Integration tests | End-to-end workflows |
| `auth` | Authentication tests | Auth endpoints and utilities |
| `permissions` | Permission tests | RBAC and protected routes |
| `models` | Database model tests | Model functionality |
| `fast` | Quick tests only | Excludes slow integration tests |

## Test Data and Fixtures

### Test Database
- Uses SQLite in-memory database for isolation
- Fresh database created for each test
- Automatic cleanup after each test

### Test Users
The test suite creates various test users:

```python
# Admin user
username: "test_admin"
password: "admin123"
roles: ["Admin"]

# Editor user  
username: "test_editor"
password: "editor123"
roles: ["Editor"]

# Viewer user
username: "test_viewer" 
password: "viewer123"
roles: ["Viewer"]

# Multi-role user
username: "test_multi"
password: "multi123"
roles: ["Editor", "Viewer"]

# No-role user
username: "test_norole"
password: "norole123"
roles: []
```

### Test Roles and Permissions
```python
# Roles with their permissions
Admin: ["can_read", "can_write", "can_delete"]
Editor: ["can_read", "can_write"]
Viewer: ["can_read"]
```

## Test Results and Reporting

### Coverage Reports
When running with `--coverage`, the test suite generates:
- Terminal coverage summary
- HTML coverage report in `htmlcov/index.html`
- Minimum coverage threshold: 80%

### Test Output
- **Passed Tests**: ✅ Green checkmarks
- **Failed Tests**: ❌ Red X marks with detailed error information
- **Skipped Tests**: ⚠️ Yellow warnings (if any)

### Performance
- **Fast Tests**: Complete in under 30 seconds
- **Full Suite**: Complete in under 2 minutes
- **Parallel Execution**: Reduces runtime by ~50%

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python run_tests.py --coverage --failfast
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

## Adding New Tests

### Test File Naming
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test Structure
```python
class TestNewFeature:
    """Test new feature functionality"""
    
    def test_feature_success_case(self, client, test_users):
        """Test successful feature usage"""
        # Arrange
        user = test_users["admin"]
        
        # Act
        response = client.get("/new-endpoint")
        
        # Assert
        assert response.status_code == 200
    
    def test_feature_failure_case(self, client):
        """Test feature failure handling"""
        # Test implementation
        pass
```

### Best Practices
1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test both success and failure cases**
4. **Use appropriate fixtures** for test data setup
5. **Keep tests independent** and isolated
6. **Test edge cases** and boundary conditions

## Troubleshooting

### Common Issues

**Database Errors**
```bash
# Clear test database
rm -f test.db
```

**Import Errors**
```bash
# Ensure you're in the project root
cd /path/to/rbac-auth-system
export PYTHONPATH=$PWD
```

**Permission Errors**
```bash
# Make test runner executable
chmod +x run_tests.py
```

### Debug Mode
```bash
# Run with Python debugger
pytest --pdb

# Run with detailed output
pytest -vvv --tb=long
```

## Test Metrics

Current test suite metrics:
- **Total Tests**: 100+ comprehensive tests
- **Test Files**: 6 specialized test modules
- **Coverage Target**: 80%+ code coverage
- **Execution Time**: < 2 minutes for full suite
- **Test Categories**: Unit, Integration, Security, Performance

The test suite ensures the RBAC Auth System is robust, secure, and reliable for production use.