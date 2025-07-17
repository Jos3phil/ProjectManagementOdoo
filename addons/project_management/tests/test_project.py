from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import date

class TestProject(TransactionCase):
    """
    Test suite for the Project Management module.
    This test class validates the project progress calculation functionality
    and ensures proper behavior of the project.management model.
    Test Cases:
    - test_compute_progress_no_tasks: Verifies progress is 0% when no tasks exist
    - test_compute_progress_all_tasks_completed: Verifies progress is 100% when all tasks are completed
    - test_compute_progress_partial_completion: Verifies correct percentage calculation with mixed task states
    - test_compute_progress_no_completed_tasks: Verifies progress is 0% when no tasks are completed
    - test_compute_progress_single_completed_task: Verifies progress is 100% with single completed task
    Setup:
    Creates a test project with admin supervisor and test executor user for task assignments.
    All tests use the same project instance to validate progress computation method.
    Dependencies:
    - project.management model
    - project.task model
    - res.users model (for executor and supervisor)
    """
    
    def setUp(self):
        super(TestProject, self).setUp()
        self.Project = self.env['project.management']
        self.Task = self.env['project.task']
        self.user = self.env.ref('base.user_admin')
        
        # Crear ejecutor para las tareas
        self.executor = self.env['res.users'].create({
            'name': 'Test Executor',
            'login': 'executor@test.com',
            'email': 'executor@test.com'
        })
        
        # Create a test project
        self.project = self.Project.create({
            'name': 'Test Project',
            'supervisor_id': self.user.id,
            'date_start': date.today(),
            'state': 'draft'
        })
    
    def test_compute_progress_no_tasks(self):
        """Test progress calculation when project has no tasks"""
        self.project._compute_progress()
        self.assertEqual(self.project.progress, 0.0)
    
    def test_compute_progress_all_tasks_completed(self):
        """Test progress calculation when all tasks are completed"""
        # Create completed tasks
        self.Task.create({
            'name': 'Task 1',
            'project_id': self.project.id,
            'executor_id': self.executor.id,  # Agregar executor_id
            'state': 'completed'
        })
        self.Task.create({
            'name': 'Task 2',
            'project_id': self.project.id,
            'executor_id': self.executor.id,  # Agregar executor_id
            'state': 'completed'
        })
        
        self.project._compute_progress()
        self.assertEqual(self.project.progress, 100.0)
    
    def test_compute_progress_partial_completion(self):
        """Test progress calculation with partial task completion"""
        # Create mixed state tasks
        self.Task.create({
            'name': 'Task 1',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        self.Task.create({
            'name': 'Task 2',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'in_progress'
        })
        self.Task.create({
            'name': 'Task 3',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'draft'
        })
        self.Task.create({
            'name': 'Task 4',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        
        self.project._compute_progress()
        self.assertEqual(self.project.progress, 50.0)  # 2 completed out of 4 total
    
    def test_compute_progress_no_completed_tasks(self):
        """Test progress calculation when no tasks are completed"""
        # Create non-completed tasks
        self.Task.create({
            'name': 'Task 1',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'draft'
        })
        self.Task.create({
            'name': 'Task 2',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'in_progress'
        })
        
        self.project._compute_progress()
        self.assertEqual(self.project.progress, 0.0)
    
    def test_compute_progress_single_completed_task(self):
        """Test progress calculation with single completed task"""
        self.Task.create({
            'name': 'Task 1',
            'project_id': self.project.id,
            'executor_id': self.executor.id,
            'state': 'completed'
        })
        
        self.project._compute_progress()
        self.assertEqual(self.project.progress, 100.0)