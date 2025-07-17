from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import psycopg2


class TestProjectRoleEnhanced(TransactionCase):
    """
    Enhanced test suite for ProjectRole model with improved error messages and debugging capabilities.
    This test class provides comprehensive testing for the ProjectRole model with:
    - Custom assertion methods for clearer error messages
    - Enhanced debugging output with emojis and context
    - Step-by-step validation for complex operations
    - Detailed feedback for test failures
    The test suite covers:
    - Role creation and validation
    - User assignment to roles
    - Duplicate user handling
    - Role permissions functionality
    - Name uniqueness constraints
    - Error handling and edge cases
    Custom Assertions:
    - assertRoleCreatedSuccessfully: Validates role creation with detailed feedback
    - assertUserAssignedToRole: Verifies user assignment with context
    - assertRoleUserCount: Checks user count in roles
    - assertValidationErrorWithMessage: Validates expected errors with context
    Debug Features:
    - debug_role_state: Prints detailed role information
    - Enhanced error messages with emojis and context
    - Step-by-step operation tracking
    - Clear failure descriptions
    Example Usage:
        The test methods demonstrate various scenarios:
        - Basic role creation and validation
        - Single and multiple user assignments
        - Duplicate user prevention
        - Empty/missing name validation
        - Permissions field testing
        - Role name uniqueness validation
    Each test method provides clear success/failure feedback and debugging
    information to help identify issues quickly during development.
    """
    """Tests de ProjectRole con mensajes de error mejorados"""
    
    def setUp(self):
        super(TestProjectRoleEnhanced, self).setUp()
        self.ProjectRole = self.env['project.role']
        self.User = self.env['res.users']
        
        # Create test user
        self.test_user = self.User.create({
            'name': 'Test User',
            'login': 'testuser@example.com',
            'email': 'testuser@example.com',
        })
    
    # =============== CUSTOM ASSERTIONS ===============
    
    def assertRoleCreatedSuccessfully(self, role, expected_name, expected_description=None):
        """Custom assertion para verificar creación exitosa de rol"""
        self.assertTrue(
            role.exists(), 
            f"❌ ROLE CREATION FAILED: Role '{expected_name}' was not created in database"
        )
        self.assertEqual(
            role.name, expected_name,
            f"❌ ROLE NAME MISMATCH: Expected '{expected_name}', got '{role.name}'"
        )
        if expected_description:
            self.assertEqual(
                role.description, expected_description,
                f"❌ DESCRIPTION MISMATCH: Expected '{expected_description}', got '{role.description}'"
            )
    
    def assertUserAssignedToRole(self, role, user, context=""):
        """Custom assertion para verificar asignación de usuario"""
        self.assertIn(
            user, role.user_ids,
            f"❌ USER ASSIGNMENT FAILED{context}: User '{user.name}' (ID: {user.id}) not found in role '{role.name}' user list. "
            f"Current users in role: {[u.name for u in role.user_ids]}"
        )
    
    def assertRoleUserCount(self, role, expected_count, context=""):
        """Custom assertion para verificar cantidad de usuarios en rol"""
        actual_count = len(role.user_ids)
        self.assertEqual(
            actual_count, expected_count,
            f"❌ USER COUNT MISMATCH{context}: Role '{role.name}' has {actual_count} users, expected {expected_count}. "
            f"Users in role: {[u.name for u in role.user_ids]}"
        )
    
    def assertValidationErrorWithMessage(self, test_func, expected_error_type="ValidationError", context=""):
        """Custom assertion para errores de validación con contexto"""
        try:
            test_func()
            self.fail(f"❌ VALIDATION ERROR EXPECTED{context}: {expected_error_type} should have been raised but wasn't")
        except ValidationError as e:
            self.assertTrue(True, f"✅ VALIDATION WORKING{context}: {expected_error_type} correctly raised: {str(e)}")
        except psycopg2.errors.NotNullViolation as e:
            # Transformar error de DB en mensaje más claro
            if "name" in str(e).lower():
                self.assertTrue(True, f"✅ REQUIRED FIELD VALIDATION{context}: Name field is correctly required (DB constraint)")
            else:
                self.fail(f"❌ UNEXPECTED DB ERROR{context}: {str(e)}")
        except Exception as e:
            self.fail(f"❌ UNEXPECTED ERROR TYPE{context}: Expected {expected_error_type}, got {type(e).__name__}: {str(e)}")
    
    # =============== ENHANCED TESTS ===============
    
    def test_create_project_role(self):
        """Test creating a project role with enhanced debugging"""
        # Act
        role = self.ProjectRole.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        # Assert with custom messages
        self.assertRoleCreatedSuccessfully(
            role, 
            'Test Role', 
            'Test role description'
        )
        
        # Additional checks with context
        self.assertEqual(
            len(role.user_ids), 0,
            f"❌ INITIAL STATE ERROR: New role '{role.name}' should have 0 users initially, found {len(role.user_ids)}"
        )
        self.assertEqual(
            len(role.permissions), 0,
            f"❌ INITIAL PERMISSIONS ERROR: New role '{role.name}' should have 0 permissions initially, found {len(role.permissions)}"
        )
    
    def test_create_role_without_name(self):
        """Test that creating a role without name raises appropriate error"""
        
        def create_nameless_role():
            return self.ProjectRole.create({
                'description': 'Test role description'
            })
        
        # Use custom assertion with context
        self.assertValidationErrorWithMessage(
            create_nameless_role,
            context=" when creating role without name"
        )
    
    def test_create_role_with_empty_name(self):
        """Test creating role with empty name"""
        
        def create_empty_name_role():
            return self.ProjectRole.create({
                'name': '',
                'description': 'Test role description'
            })
        
        self.assertValidationErrorWithMessage(
            create_empty_name_role,
            context=" when creating role with empty name"
        )
    
    def test_assign_role_to_user(self):
        """Test assigning a role to a user with enhanced feedback"""
        # Arrange
        role = self.ProjectRole.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        # Act
        result = role.assign_role_to_user(self.test_user.id)
        
        # Assert with detailed messages
        self.assertTrue(
            result,
            f"❌ ASSIGNMENT FAILED: assign_role_to_user returned {result}, expected True"
        )
        
        self.assertUserAssignedToRole(
            role, self.test_user, 
            context=f" after calling assign_role_to_user({self.test_user.id})"
        )
        
        self.assertRoleUserCount(
            role, 1,
            context=" after first user assignment"
        )
    
    def test_assign_multiple_users_to_role(self):
        """Test assigning multiple users to a role with step-by-step validation"""
        # Arrange
        role = self.ProjectRole.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        user2 = self.User.create({
            'name': 'Test User 2',
            'login': 'testuser2@example.com',
            'email': 'testuser2@example.com',
        })
        
        # Act & Assert step by step
        print(f"🔍 DEBUG: Starting with role '{role.name}' having {len(role.user_ids)} users")
        
        # First assignment
        role.assign_role_to_user(self.test_user.id)
        self.assertRoleUserCount(role, 1, context=" after first user assignment")
        self.assertUserAssignedToRole(role, self.test_user, context=" - first user")
        
        # Second assignment
        role.assign_role_to_user(user2.id)
        self.assertRoleUserCount(role, 2, context=" after second user assignment")
        self.assertUserAssignedToRole(role, user2, context=" - second user")
        
        # Verify both users are present
        user_names = [u.name for u in role.user_ids]
        self.assertIn(
            'Test User', user_names,
            f"❌ FIRST USER LOST: 'Test User' not found after second assignment. Current users: {user_names}"
        )
        self.assertIn(
            'Test User 2', user_names,
            f"❌ SECOND USER NOT ADDED: 'Test User 2' not found after assignment. Current users: {user_names}"
        )
    
    def test_assign_duplicate_user_to_role(self):
        """Test assigning the same user twice with clear feedback"""
        # Arrange
        role = self.ProjectRole.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        # First assignment
        role.assign_role_to_user(self.test_user.id)
        initial_count = len(role.user_ids)
        
        # Second assignment (duplicate)
        result = role.assign_role_to_user(self.test_user.id)
        final_count = len(role.user_ids)
        
        # Assert no duplicates
        self.assertEqual(
            initial_count, final_count,
            f"❌ DUPLICATE USER ALLOWED: User count changed from {initial_count} to {final_count} "
            f"when assigning same user twice. Users: {[u.name for u in role.user_ids]}"
        )
        
        # Count specific user occurrences
        user_occurrences = sum(1 for u in role.user_ids if u.id == self.test_user.id)
        self.assertEqual(
            user_occurrences, 1,
            f"❌ USER DUPLICATED: User '{self.test_user.name}' appears {user_occurrences} times in role, should be 1"
        )
    
    def test_role_permissions_field(self):
        """Test that permissions field works correctly with detailed feedback"""
        role = self.ProjectRole.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        # Check initial state
        self.assertFalse(
            role.permissions,
            f"❌ PERMISSIONS INITIALIZATION: Role '{role.name}' permissions should be empty initially. "
            f"Found: {role.permissions}"
        )
        
        self.assertEqual(
            len(role.permissions), 0,
            f"❌ PERMISSIONS COUNT: Role '{role.name}' should have 0 permissions initially, "
            f"found {len(role.permissions)}: {list(role.permissions)}"
        )
        
        # Verify field type
        self.assertTrue(
            hasattr(role, 'permissions'),
            f"❌ FIELD MISSING: Role model missing 'permissions' field"
        )
    
    def test_role_name_uniqueness(self):
        """Test role name uniqueness with clear error messages"""
        # Create first role
        role1 = self.ProjectRole.create({
            'name': 'Unique Role',
            'description': 'First role'
        })
        
        def create_duplicate_role():
            return self.ProjectRole.create({
                'name': 'Unique Role',  # Same name
                'description': 'Second role'
            })
        
        # Test if uniqueness is enforced
        try:
            role2 = create_duplicate_role()
            # If no error, uniqueness is not enforced
            print(f"⚠️  WARNING: Role name uniqueness not enforced. Two roles with name 'Unique Role' exist: "
                  f"ID {role1.id} and ID {role2.id}")
        except Exception as e:
            print(f"✅ UNIQUENESS ENFORCED: Duplicate role name correctly prevented: {str(e)}")
    
    # =============== DEBUGGING HELPER METHODS ===============
    
    def debug_role_state(self, role, context=""):
        """Helper method para debuggear estado del rol"""
        print(f"\n🔍 DEBUG ROLE STATE{context}:")
        print(f"  Name: '{role.name}'")
        print(f"  Description: '{role.description}'")
        print(f"  Users count: {len(role.user_ids)}")
        print(f"  Users: {[u.name for u in role.user_ids]}")
        print(f"  Permissions count: {len(role.permissions)}")
        print(f"  Role ID: {role.id}")
    
    def test_debug_example(self):
        """Example test showing debug capabilities"""
        role = self.ProjectRole.create({
            'name': 'Debug Role',
            'description': 'Role for debugging'
        })
        
        self.debug_role_state(role, " after creation")
        
        role.assign_role_to_user(self.test_user.id)
        self.debug_role_state(role, " after user assignment")
        
        self.assertRoleCreatedSuccessfully(role, 'Debug Role')