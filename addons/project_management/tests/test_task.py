from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class TestTask(TransactionCase):
    """
    Test suite for project.task model functionality.
    This test class validates the core functionality of project tasks including:
    - Task creation and field validation
    - Date validation constraints
    - State transitions (start, complete, cancel)
    - Required field validation
    Test Methods:
        setUp: Initialize test data including supervisor, project, and user
        test_task_creation: Verify task creation with proper field assignment
        test_end_date_validation_valid: Test valid date range acceptance
        test_end_date_validation_invalid: Test invalid date range rejection
        test_action_start: Verify task state transition to 'in_progress'
        test_action_complete: Verify task state transition to 'completed'
        test_action_cancel: Verify task state transition to 'cancelled'
        test_required_fields: Validate required field constraints
    """

    def setUp(self):
        super(TestTask, self).setUp()
        self.supervisor = self.env['res.users'].create({
            'name': 'Test Supervisor',
            'login': 'supervisor@example.com',
            'email': 'supervisor@example.com'
        })
        
        self.project = self.env['project.management'].create({
            'name': 'Test Project',
            'supervisor_id': self.supervisor.id,
            'date_start': date.today()
        })
        self.user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser'
        })

    def test_task_creation(self):
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'executor_id': self.user.id,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=5)
        })
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.state, 'draft')
        self.assertEqual(task.project_id, self.project)
        self.assertEqual(task.executor_id, self.user)

    def test_end_date_validation_valid(self):
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'executor_id': self.user.id,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=5)
        })
        # Should not raise exception
        self.assertTrue(task)

    def test_end_date_validation_invalid(self):
        with self.assertRaises(ValidationError):
            self.env['project.task'].create({
                'name': 'Test Task',
                'project_id': self.project.id,
                'executor_id': self.user.id,
                'date_start': date.today(),
                'date_end': date.today() - timedelta(days=1)
            })

    def test_action_start(self):
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'executor_id': self.user.id
        })
        task.action_start()
        self.assertEqual(task.state, 'in_progress')

    def test_action_complete(self):
        task = self.env['project.task'].create({
            'name':'Test Task',
            'project_id': self.project.id,
            'executor_id': self.user.id
        })
        task.action_complete()
        self.assertEqual(task.state, 'completed')

    def test_action_cancel(self):
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'executor_id': self.user.id
        })
        task.action_cancel()
        self.assertEqual(task.state, 'cancelled')

    def test_required_fields(self):
        with self.assertRaises(Exception):
            try:
                self.env['project.task'].create({
                    'name': 'Test Task',
                    
                })
            except Exception as e:
                self.assertIn('required', str(e))
                raise e
           