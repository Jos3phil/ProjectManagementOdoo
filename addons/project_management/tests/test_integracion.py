from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta
import psycopg2


class TestIntegracion(TransactionCase):
    """Tests de integración unificados para Project Management"""
    
    def setUp(self):
        super(TestIntegracion, self).setUp()
        
        # Modelos
        self.Project = self.env['project.management']
        self.Task = self.env['project.task']
        self.Role = self.env['project.role']
        self.User = self.env['res.users']
        
        # Usuarios de prueba
        self.supervisor = self.User.create({
            'name': 'Test Supervisor',
            'login': 'supervisor@test.com',
            'email': 'supervisor@test.com'
        })
        
        self.executor = self.User.create({
            'name': 'Test Executor',
            'login': 'executor@test.com',
            'email': 'executor@test.com'
        })
    
    # =============== CUSTOM ASSERTIONS SIMPLES ===============
    
    def assertCreated(self, record, name, context=""):
        """Assert simple para verificar creación"""
        self.assertTrue(record.exists(), f"❌ {context}: '{name}' no fue creado")
        self.assertEqual(record.name, name, f"❌ {context}: Nombre esperado '{name}', obtuvo '{record.name}'")
    
    def assertState(self, record, expected_state, context=""):
        """Assert simple para verificar estado"""
        self.assertEqual(
            record.state, expected_state,
            f"❌ {context}: Estado esperado '{expected_state}', obtuvo '{record.state}'"
        )
    
    def assertCount(self, collection, expected_count, context=""):
        """Assert simple para verificar cantidad"""
        actual = len(collection)
        self.assertEqual(
            actual, expected_count,
            f"❌ {context}: Esperado {expected_count} elementos, obtuvo {actual}"
        )
    
    def assertProgress(self, project, expected_progress, context=""):
        """Assert simple para verificar progreso"""
        self.assertEqual(
            project.progress, expected_progress,
            f"❌ {context}: Progreso esperado {expected_progress}%, obtuvo {project.progress}%"
        )
    
    def assertRequiredField(self, model, data, field_name, context=""):
        """Assert simple para campos requeridos"""
        try:
            model.create(data)
            self.fail(f"❌ {context}: Campo '{field_name}' debería ser requerido")
        except (ValidationError, psycopg2.errors.NotNullViolation):
            pass  # ✅ Error esperado
        except Exception as e:
            if 'required' in str(e).lower():
                pass  # ✅ Error esperado
            else:
                raise e
    
    def assertUserInRole(self, role, user, context=""):
        """Assert simple para verificar usuario en rol"""
        self.assertIn(user, role.user_ids, f"❌ {context}: Usuario '{user.name}' no está en rol '{role.name}'")
    
    def assertRelationship(self, child, parent, context=""):
        """Assert simple para verificar relaciones"""
        self.assertEqual(child.project_id, parent, f"❌ {context}: Relación incorrecta")
    
    # =============== TESTS DE PROJECT (basados en test_project.py) ===============
    
    def test_project_progress_no_tasks(self):
        """Test progress calculation when project has no tasks"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today(),
            'state': 'draft'
        })
        
        project._compute_progress()
        self.assertProgress(project, 0.0, "PROJECT NO TASKS")
    
    def test_project_progress_all_completed(self):
        """Test progress calculation when all tasks are completed"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today(),
            'state': 'draft'
        })
        
        # Create completed tasks
        self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        self.Task.create({
            'name': 'Task 2',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        
        project._compute_progress()
        self.assertProgress(project, 100.0, "PROJECT ALL COMPLETED")
    
    def test_project_progress_partial_completion(self):
        """Test progress calculation with partial task completion"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today(),
            'state': 'draft'
        })
        
        # Create mixed state tasks
        self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        self.Task.create({
            'name': 'Task 2',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'in_progress'
        })
        self.Task.create({
            'name': 'Task 3',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'draft'
        })
        self.Task.create({
            'name': 'Task 4',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        
        project._compute_progress()
        self.assertProgress(project, 50.0, "PROJECT PARTIAL COMPLETION")  # 2 completed out of 4 total
    
    def test_project_progress_no_completed_tasks(self):
        """Test progress calculation when no tasks are completed"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today(),
            'state': 'draft'
        })
        
        # Create non-completed tasks
        self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'draft'
        })
        self.Task.create({
            'name': 'Task 2',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'in_progress'
        })
        
        project._compute_progress()
        self.assertProgress(project, 0.0, "PROJECT NO COMPLETED TASKS")
    
    def test_project_progress_single_completed_task(self):
        """Test progress calculation with single completed task"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today(),
            'state': 'draft'
        })
        
        self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        
        project._compute_progress()
        self.assertProgress(project, 100.0, "PROJECT SINGLE COMPLETED")
    
    # =============== TESTS DE TASK (basados en test_task.py) ===============
    
    def test_task_creation(self):
        """Test task creation with proper field assignment"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=5)
        })
        
        self.assertCreated(task, 'Test Task', "TASK CREATION")
        self.assertState(task, 'draft', "TASK INITIAL STATE")
        self.assertRelationship(task, project, "TASK PROJECT RELATIONSHIP")
        self.assertEqual(task.executor_id, self.executor, f"❌ TASK EXECUTOR: Esperado {self.executor.name}, obtuvo {task.executor_id.name}")
    
    def test_task_date_validation_valid(self):
        """Test valid date range acceptance"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': project.id,
            'executor_id': self.executor.id,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=5)
        })
        # Should not raise exception
        self.assertTrue(task.exists(), "❌ TASK VALID DATES: Tarea con fechas válidas no fue creada")
    
    def test_task_date_validation_invalid(self):
        """Test invalid date range rejection"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        with self.assertRaises(ValidationError, msg="❌ DATE VALIDATION: Fecha fin anterior a inicio debería fallar"):
            self.Task.create({
                'name': 'Test Task',
                'project_id': project.id,
                'executor_id': self.executor.id,
                'date_start': date.today(),
                'date_end': date.today() - timedelta(days=1)
            })
    
    def test_task_action_start(self):
        """Test task state transition to 'in_progress'"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        task.action_start()
        self.assertState(task, 'in_progress', "TASK ACTION START")
    
    def test_task_action_complete(self):
        """Test task state transition to 'completed'"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        task.action_complete()
        self.assertState(task, 'completed', "TASK ACTION COMPLETE")
    
    def test_task_action_cancel(self):
        """Test task state transition to 'cancelled'"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        task = self.Task.create({
            'name': 'Test Task',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        task.action_cancel()
        self.assertState(task, 'cancelled', "TASK ACTION CANCEL")
    
    def test_task_required_fields(self):
        """Test required field validation for tasks"""
        project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        # Test missing name
        self.assertRequiredField(
            self.Task,
            {'project_id': project.id, 'executor_id': self.executor.id},
            'name',
            "TASK REQUIRED NAME"
        )
        
        # Test missing executor
        self.assertRequiredField(
            self.Task,
            {'name': 'Test Task', 'project_id': project.id},
            'executor_id',
            "TASK REQUIRED EXECUTOR"
        )
    
    # =============== TESTS DE ROLE (basados en test_role.py) ===============
    
    def test_role_creation(self):
        """Test creating a project role"""
        role = self.Role.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        self.assertCreated(role, 'Test Role', "ROLE CREATION")
        self.assertEqual(role.description, 'Test role description', f"❌ ROLE DESCRIPTION: Esperado 'Test role description', obtuvo '{role.description}'")
        self.assertCount(role.user_ids, 0, "ROLE INITIAL USERS")
        self.assertCount(role.permissions, 0, "ROLE INITIAL PERMISSIONS")
    
    def test_role_required_name(self):
        """Test that creating a role without name raises error"""
        self.assertRequiredField(
            self.Role,
            {'description': 'Test role description'},
            'name',
            "ROLE REQUIRED NAME"
        )
    
    def test_role_assign_user(self):
        """Test assigning a role to a user"""
        role = self.Role.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        result = role.assign_role_to_user(self.executor.id)
        
        self.assertTrue(result, f"❌ ROLE ASSIGNMENT: assign_role_to_user debería retornar True, obtuvo {result}")
        self.assertUserInRole(role, self.executor, "ROLE USER ASSIGNMENT")
        self.assertCount(role.user_ids, 1, "ROLE USER COUNT AFTER ASSIGNMENT")
    
    def test_role_multiple_users(self):
        """Test assigning multiple users to a role"""
        role = self.Role.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        # Assign multiple users
        role.assign_role_to_user(self.supervisor.id)
        role.assign_role_to_user(self.executor.id)
        
        self.assertCount(role.user_ids, 2, "ROLE MULTIPLE USERS")
        self.assertUserInRole(role, self.supervisor, "ROLE SUPERVISOR ASSIGNMENT")
        self.assertUserInRole(role, self.executor, "ROLE EXECUTOR ASSIGNMENT")
    
    def test_role_permissions_field(self):
        """Test that permissions field works correctly"""
        role = self.Role.create({
            'name': 'Test Role',
            'description': 'Test role description'
        })
        
        # Check initial state
        self.assertFalse(role.permissions, f"❌ ROLE PERMISSIONS: Permisos deberían estar vacíos inicialmente")
        self.assertCount(role.permissions, 0, "ROLE INITIAL PERMISSIONS COUNT")
        
        # Verify field exists
        self.assertTrue(hasattr(role, 'permissions'), f"❌ ROLE FIELD: Campo 'permissions' no existe")
    
    # =============== TESTS DE INTEGRACIÓN COMPLETA ===============
    
    def test_complete_workflow(self):
        """Test del flujo completo de trabajo integrado"""
        # 1. Crear rol y asignar usuario
        role = self.Role.create({
            'name': 'Project Manager',
            'description': 'Manages projects'
        })
        role.assign_role_to_user(self.supervisor.id)
        
        # 2. Crear proyecto
        project = self.Project.create({
            'name': 'Integration Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        # 3. Crear tareas
        task1 = self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        task2 = self.Task.create({
            'name': 'Task 2',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        # 4. Verificar estados iniciales
        self.assertState(project, 'draft', "WORKFLOW INITIAL PROJECT STATE")
        self.assertState(task1, 'draft', "WORKFLOW INITIAL TASK1 STATE")
        self.assertState(task2, 'draft', "WORKFLOW INITIAL TASK2 STATE")
        
        # 5. Iniciar proyecto y una tarea
        project.action_start()
        task1.action_start()
        
        self.assertState(project, 'in_progress', "WORKFLOW PROJECT STARTED")
        self.assertState(task1, 'in_progress', "WORKFLOW TASK1 STARTED")
        
        # 6. Completar una tarea y verificar progreso
        task1.action_complete()
        project._compute_progress()
        self.assertProgress(project, 50.0, "WORKFLOW PARTIAL PROGRESS")
        
        # 7. Completar segunda tarea y proyecto
        task2.action_complete()
        project._compute_progress()
        self.assertProgress(project, 100.0, "WORKFLOW FULL PROGRESS")
        
        project.action_complete()
        self.assertState(project, 'completed', "WORKFLOW PROJECT COMPLETED")
        
        # 8. Verificaciones finales
        self.assertCount(project.task_ids, 2, "WORKFLOW FINAL TASK COUNT")
        self.assertUserInRole(role, self.supervisor, "WORKFLOW FINAL ROLE ASSIGNMENT")
        self.assertRelationship(task1, project, "WORKFLOW TASK1 RELATIONSHIP")
        self.assertRelationship(task2, project, "WORKFLOW TASK2 RELATIONSHIP")
    
    def test_project_task_relationship(self):
        """Test relación One2many entre proyecto y tareas"""
        project = self.Project.create({
            'name': 'Relationship Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        # Crear múltiples tareas
        tasks = []
        for i in range(3):
            task = self.Task.create({
                'name': f'Task {i+1}',
                'project_id': project.id,
                'executor_id': self.executor.id
            })
            tasks.append(task)
        
        # Verificar relación One2many
        self.assertCount(project.task_ids, 3, "PROJECT TASK RELATIONSHIP")
        
        # Verificar que todas las tareas están vinculadas
        for task in tasks:
            self.assertIn(task, project.task_ids, f"❌ RELATIONSHIP: Tarea '{task.name}' no está en project.task_ids")
            self.assertRelationship(task, project, f"REVERSE RELATIONSHIP {task.name}")

    # =============== TESTS DE INTEGRACIÓN COMPLETA ===============
    
    def test_complete_workflow(self):
        """Test del flujo completo de trabajo"""
        # 1. Crear rol
        role = self.Role.create({
            'name': 'Project Manager',
            'description': 'Manages projects'
        })
        role.assign_role_to_user(self.supervisor.id)
        
        # 2. Crear proyecto
        project = self.Project.create({
            'name': 'Integration Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        # 3. Crear tareas
        task1 = self.Task.create({
            'name': 'Task 1',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        task2 = self.Task.create({
            'name': 'Task 2',
            'project_id': project.id,
            'executor_id': self.executor.id
        })
        
        # 4. Iniciar proyecto
        project.action_start()
        self.assertState(project, 'in_progress', "WORKFLOW PROJECT START")
        
        # 5. Completar una tarea
        task1.action_complete()
        project._compute_progress()
        self.assertProgress(project, 50.0, "WORKFLOW PARTIAL PROGRESS")
        
        # 6. Completar segunda tarea
        task2.action_complete()
        project._compute_progress()
        self.assertProgress(project, 100.0, "WORKFLOW FULL PROGRESS")
        
        # 7. Completar proyecto
        project.action_complete()
        self.assertState(project, 'completed', "WORKFLOW PROJECT COMPLETION")
        
        # Verificaciones finales
        self.assertCount(project.task_ids, 2, "WORKFLOW FINAL TASK COUNT")
        self.assertIn(self.supervisor, role.user_ids, "WORKFLOW ROLE ASSIGNMENT")
    
    def test_project_task_relationship(self):
        """Test relación entre proyecto y tareas"""
        project = self.Project.create({
            'name': 'Relationship Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        
        # Crear múltiples tareas
        tasks = []
        for i in range(3):
            task = self.Task.create({
                'name': f'Task {i+1}',
                'project_id': project.id,
                'executor_id': self.executor.id
            })
            tasks.append(task)
        
        # Verificar relación One2many
        self.assertCount(project.task_ids, 3, "PROJECT TASK RELATIONSHIP")
        
        # Verificar que todas las tareas están vinculadas
        for task in tasks:
            self.assertIn(task, project.task_ids, f"TASK {task.name} IN PROJECT")
            self.assertEqual(task.project_id, project, f"REVERSE RELATIONSHIP {task.name}")
    
    # =============== HELPER METHOD ===============
    
    def debug_state(self, context=""):
        """Helper para debugging durante desarrollo"""
        if context:
            print(f"\n🔍 DEBUG {context}:")
            print(f"  Projects: {self.Project.search_count([])}")
            print(f"  Tasks: {self.Task.search_count([])}")
            print(f"  Roles: {self.Role.search_count([])}")
            print(f"  Users: {self.User.search_count([])}")