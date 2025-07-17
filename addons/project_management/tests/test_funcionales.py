from odoo.tests.common import HttpCase, TransactionCase
from odoo.tests import tagged
from datetime import date, timedelta
import json


@tagged('functional', 'project_management')
class TestProjectManagementFunctional(HttpCase):
    """
    Pruebas funcionales completas del sistema Project Management
    Simulan flujos reales de usuario desde la interfaz web
    """
    
    def setUp(self):
        super().setUp()
        
        # Crear usuarios con roles específicos
        self.manager_user = self.env['res.users'].create({
            'name': 'Project Manager',
            'login': 'manager@company.com',
            'email': 'manager@company.com',
            'password': 'manager123',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
        
        self.developer_user = self.env['res.users'].create({
            'name': 'Developer',
            'login': 'dev@company.com', 
            'email': 'dev@company.com',
            'password': 'dev123',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })

    def test_complete_project_lifecycle_workflow(self):
        """
        FLUJO FUNCIONAL COMPLETO: Ciclo de vida de un proyecto
        Simula: Manager crea proyecto → Asigna tareas → Developer ejecuta → Proyecto completo
        """
        
        # ============ PASO 1: MANAGER LOGIN ============
        self.authenticate('manager@company.com', 'manager123')
        
        # ============ PASO 2: CREAR PROYECTO VIA WEB ============
        project_data = {
            'name': 'Website Redesign Project',
            'supervisor_id': self.manager_user.id,
            'date_start': date.today().isoformat(),
            'date_end': (date.today() + timedelta(days=30)).isoformat(),
            'description': '<p>Complete website redesign for better UX</p>',
            'state': 'draft'
        }
        
        # Simular creación desde formulario web
        response = self.url_open('/web/dataset/call_kw/project.management/create', {
            'model': 'project.management',
            'method': 'create',
            'args': [project_data],
            'kwargs': {}
        })
        
        self.assertEqual(response.status_code, 200, "❌ FUNCTIONAL: No se pudo crear proyecto via web")
        
        # Verificar que el proyecto existe en DB
        project = self.env['project.management'].search([('name', '=', 'Website Redesign Project')])
        self.assertTrue(project.exists(), "❌ FUNCTIONAL: Proyecto no se guardó en base de datos")
        
        # ============ PASO 3: CREAR TAREAS DEL PROYECTO ============
        tasks_data = [
            {
                'name': 'Design Mockups',
                'project_id': project.id,
                'executor_id': self.developer_user.id,
                'date_start': date.today().isoformat(),
                'date_end': (date.today() + timedelta(days=7)).isoformat(),
                'description': 'Create initial design mockups'
            },
            {
                'name': 'Frontend Development', 
                'project_id': project.id,
                'executor_id': self.developer_user.id,
                'date_start': (date.today() + timedelta(days=7)).isoformat(),
                'date_end': (date.today() + timedelta(days=21)).isoformat(),
                'description': 'Implement frontend based on mockups'
            },
            {
                'name': 'Testing & Deploy',
                'project_id': project.id,
                'executor_id': self.manager_user.id,
                'date_start': (date.today() + timedelta(days=21)).isoformat(), 
                'date_end': (date.today() + timedelta(days=30)).isoformat(),
                'description': 'Test and deploy to production'
            }
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            task = self.env['project.task'].create(task_data)
            created_tasks.append(task)
            
        # Verificar que las tareas están vinculadas al proyecto
        self.assertEqual(len(project.task_ids), 3, "❌ FUNCTIONAL: No se crearon todas las tareas")
        self.assertEqual(project.progress, 0.0, "❌ FUNCTIONAL: Progreso inicial debe ser 0%")
        
        # ============ PASO 4: INICIAR PROYECTO ============
        project.action_start()
        self.assertEqual(project.state, 'in_progress', "❌ FUNCTIONAL: Proyecto no cambió a in_progress")
        
        # ============ PASO 5: DEVELOPER LOGIN Y TRABAJO EN TAREAS ============
        self.authenticate('dev@company.com', 'dev123')
        
        # Developer inicia primera tarea
        task_design = created_tasks[0]
        task_design.action_start()
        self.assertEqual(task_design.state, 'in_progress', "❌ FUNCTIONAL: Tarea no inició")
        
        # Simular trabajo y completar tarea
        task_design.action_complete()
        self.assertEqual(task_design.state, 'completed', "❌ FUNCTIONAL: Tarea no se completó")
        self.assertEqual(project.progress, 33.33, "❌ FUNCTIONAL: Progreso no se actualizó (33.33%)")
        
        # Developer trabaja en segunda tarea
        task_frontend = created_tasks[1]
        task_frontend.action_start()
        task_frontend.action_complete()
        self.assertEqual(project.progress, 66.67, "❌ FUNCTIONAL: Progreso no se actualizó (66.67%)")
        
        # ============ PASO 6: MANAGER FINALIZA PROYECTO ============
        self.authenticate('manager@company.com', 'manager123')
        
        # Manager completa última tarea
        task_testing = created_tasks[2]
        task_testing.action_start()
        task_testing.action_complete()
        self.assertEqual(project.progress, 100.0, "❌ FUNCTIONAL: Progreso no llegó a 100%")
        
        # Manager marca proyecto como completado
        project.action_complete()
        self.assertEqual(project.state, 'completed', "❌ FUNCTIONAL: Proyecto no se marcó como completado")
        
        # ============ VERIFICACIÓN FINAL DEL FLUJO ============
        self.assertTrue(all(task.state == 'completed' for task in created_tasks), 
                       "❌ FUNCTIONAL: No todas las tareas están completadas")
        
        print("✅ FUNCTIONAL SUCCESS: Flujo completo de proyecto ejecutado correctamente")

    def test_user_role_management_workflow(self):
        """
        FLUJO FUNCIONAL: Gestión de roles y permisos
        Simula: Admin crea roles → Asigna usuarios → Verifica permisos
        """
        
        # ============ CREAR ROLES DEL SISTEMA ============
        project_manager_role = self.env['project.role'].create({
            'name': 'Project Manager',
            'description': 'Can create and manage projects, assign tasks'
        })
        
        developer_role = self.env['project.role'].create({
            'name': 'Developer',
            'description': 'Can work on assigned tasks'
        })
        
        # ============ ASIGNAR USUARIOS A ROLES ============
        project_manager_role.assign_role_to_user(self.manager_user.id)
        developer_role.assign_role_to_user(self.developer_user.id)
        
        # ============ VERIFICAR ASIGNACIONES ============
        self.assertIn(self.manager_user, project_manager_role.user_ids,
                     "❌ FUNCTIONAL: Manager no asignado a rol Project Manager")
        self.assertIn(self.developer_user, developer_role.user_ids,
                     "❌ FUNCTIONAL: Developer no asignado a rol Developer")
        
        # ============ SIMULAR CONTROL DE ACCESO ============
        # Manager puede crear proyectos
        self.authenticate('manager@company.com', 'manager123')
        
        try:
            manager_project = self.env['project.management'].create({
                'name': 'Manager Created Project',
                'supervisor_id': self.manager_user.id,
                'date_start': date.today()
            })
            manager_can_create = True
        except:
            manager_can_create = False
            
        self.assertTrue(manager_can_create, "❌ FUNCTIONAL: Manager no puede crear proyectos")
        
        # Developer puede trabajar en tareas asignadas
        self.authenticate('dev@company.com', 'dev123') 
        
        task = self.env['project.task'].create({
            'name': 'Developer Task',
            'project_id': manager_project.id,
            'executor_id': self.developer_user.id
        })
        
        task.action_start()
        self.assertEqual(task.state, 'in_progress', "❌ FUNCTIONAL: Developer no puede iniciar tareas")
        
        print("✅ FUNCTIONAL SUCCESS: Gestión de roles funcionando correctamente")

    def test_task_validation_and_error_handling(self):
        """
        FLUJO FUNCIONAL: Validaciones y manejo de errores
        Simula: Usuario intenta crear datos inválidos → Sistema rechaza → Mensajes claros
        """
        
        self.authenticate('manager@company.com', 'manager123')
        
        # ============ CREAR PROYECTO BASE ============
        project = self.env['project.management'].create({
            'name': 'Validation Test Project',
            'supervisor_id': self.manager_user.id,
            'date_start': date.today()
        })
        
        # ============ TEST 1: FECHAS INVÁLIDAS ============
        try:
            invalid_task = self.env['project.task'].create({
                'name': 'Invalid Date Task',
                'project_id': project.id,
                'executor_id': self.developer_user.id,
                'date_start': date.today(),
                'date_end': date.today() - timedelta(days=1)  # Fecha fin anterior a inicio
            })
            date_validation_working = False
        except Exception as e:
            date_validation_working = True
            self.assertIn('earlier', str(e).lower(), "❌ FUNCTIONAL: Mensaje de error no es claro")
            
        self.assertTrue(date_validation_working, "❌ FUNCTIONAL: Validación de fechas no funciona")
        
        # ============ TEST 2: CAMPOS REQUERIDOS ============
        try:
            self.env['project.task'].create({
                'project_id': project.id,
                'executor_id': self.developer_user.id
                # Sin nombre - campo requerido
            })
            required_validation_working = False
        except:
            required_validation_working = True
            
        self.assertTrue(required_validation_working, "❌ FUNCTIONAL: Validación de campos requeridos no funciona")
        
        # ============ TEST 3: RELACIONES VÁLIDAS ============
        valid_task = self.env['project.task'].create({
            'name': 'Valid Task',
            'project_id': project.id,
            'executor_id': self.developer_user.id,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=5)
        })
        
        self.assertEqual(valid_task.project_id, project, "❌ FUNCTIONAL: Relación proyecto-tarea no funciona")
        self.assertIn(valid_task, project.task_ids, "❌ FUNCTIONAL: Relación inversa no funciona")
        
        print("✅ FUNCTIONAL SUCCESS: Validaciones y manejo de errores funcionando")

    def test_progress_calculation_realtime(self):
        """
        FLUJO FUNCIONAL: Cálculo de progreso en tiempo real
        Simula: Usuario completa tareas → Progreso se actualiza automáticamente
        """
        
        self.authenticate('manager@company.com', 'manager123')
        
        # ============ SETUP: PROYECTO CON 5 TAREAS ============
        project = self.env['project.management'].create({
            'name': 'Progress Test Project',
            'supervisor_id': self.manager_user.id,
            'date_start': date.today()
        })
        
        tasks = []
        for i in range(5):
            task = self.env['project.task'].create({
                'name': f'Task {i+1}',
                'project_id': project.id,
                'executor_id': self.developer_user.id
            })
            tasks.append(task)
            
        # ============ VERIFICAR PROGRESO INICIAL ============
        self.assertEqual(project.progress, 0.0, "❌ FUNCTIONAL: Progreso inicial debe ser 0%")
        
        # ============ COMPLETAR TAREAS GRADUALMENTE ============
        progress_checkpoints = [20.0, 40.0, 60.0, 80.0, 100.0]
        
        for i, task in enumerate(tasks):
            task.action_complete()
            expected_progress = progress_checkpoints[i]
            
            # Verificar que el progreso se actualiza inmediatamente
            actual_progress = project.progress
            self.assertEqual(actual_progress, expected_progress, 
                           f"❌ FUNCTIONAL: Progreso esperado {expected_progress}%, obtuvo {actual_progress}%")
            
            print(f"✅ STEP {i+1}: Tarea completada, progreso: {actual_progress}%")
        
        # ============ VERIFICAR ESTADO FINAL ============
        self.assertEqual(project.progress, 100.0, "❌ FUNCTIONAL: Progreso final debe ser 100%")
        self.assertTrue(all(task.state == 'completed' for task in tasks),
                       "❌ FUNCTIONAL: Todas las tareas deben estar completadas")
        
        print("✅ FUNCTIONAL SUCCESS: Cálculo de progreso en tiempo real funcionando")

    def test_concurrent_user_workflow(self):
        """
        FLUJO FUNCIONAL: Múltiples usuarios trabajando simultáneamente
        Simula: Manager y Developer trabajando en el mismo proyecto simultáneamente
        """
        
        # ============ SETUP: PROYECTO COMPARTIDO ============
        project = self.env['project.management'].create({
            'name': 'Concurrent Work Project',
            'supervisor_id': self.manager_user.id,
            'date_start': date.today()
        })
        
        # Manager crea tareas
        self.authenticate('manager@company.com', 'manager123')
        
        manager_task = self.env['project.task'].create({
            'name': 'Manager Task',
            'project_id': project.id,
            'executor_id': self.manager_user.id
        })
        
        developer_task = self.env['project.task'].create({
            'name': 'Developer Task', 
            'project_id': project.id,
            'executor_id': self.developer_user.id
        })
        
        # ============ TRABAJO CONCURRENTE ============
        # Manager inicia proyecto
        project.action_start()
        self.assertEqual(project.state, 'in_progress', "❌ FUNCTIONAL: Manager no pudo iniciar proyecto")
        
        # Developer trabaja en su tarea
        self.authenticate('dev@company.com', 'dev123')
        developer_task.action_start()
        developer_task.action_complete()
        
        # Manager trabaja en su tarea
        self.authenticate('manager@company.com', 'manager123')
        manager_task.action_start()
        manager_task.action_complete()
        
        # ============ VERIFICAR SINCRONIZACIÓN ============
        self.assertEqual(project.progress, 100.0, "❌ FUNCTIONAL: Progreso no se sincronizó correctamente")
        self.assertEqual(len(project.task_ids), 2, "❌ FUNCTIONAL: No se mantuvieron ambas tareas")
        
        # Ambos usuarios pueden ver el estado final
        for user_login in ['manager@company.com', 'dev@company.com']:
            self.authenticate(user_login, user_login.split('@')[0] + '123')
            
            # Verificar que pueden acceder al proyecto actualizado
            current_project = self.env['project.management'].browse(project.id)
            self.assertEqual(current_project.progress, 100.0,
                           f"❌ FUNCTIONAL: Usuario {user_login} no ve progreso actualizado")
        
        print("✅ FUNCTIONAL SUCCESS: Trabajo concurrente funcionando correctamente")


# =============== HELPER PARA EJECUTAR SOLO TESTS FUNCIONALES ===============

@tagged('functional_only')  
class TestProjectManagementFunctionalOnly(TransactionCase):
    """
    Pruebas funcionales simplificadas sin HTTP (más rápidas)
    Para CI/CD donde no se necesita interfaz web completa
    """
    
    def test_end_to_end_business_logic(self):
        """Test completo de lógica de negocio sin interfaz web"""
        
        # Crear usuarios
        manager = self.env['res.users'].create({
            'name': 'Manager', 'login': 'manager', 'email': 'manager@test.com'
        })
        developer = self.env['res.users'].create({
            'name': 'Developer', 'login': 'dev', 'email': 'dev@test.com'
        })
        
        # Flujo completo de negocio
        project = self.env['project.management'].create({
            'name': 'Business Logic Test',
            'supervisor_id': manager.id,
            'date_start': date.today()
        })
        
        # Crear tareas
        tasks = []
        for i in range(3):
            task = self.env['project.task'].create({
                'name': f'Business Task {i+1}',
                'project_id': project.id,
                'executor_id': developer.id
            })
            tasks.append(task)
        
        # Ejecutar flujo
        project.action_start()
        
        for task in tasks:
            task.action_start()
            task.action_complete()
            
        project.action_complete()
        
        # Verificaciones finales
        self.assertEqual(project.state, 'completed')
        self.assertEqual(project.progress, 100.0)
        self.assertTrue(all(t.state == 'completed' for t in tasks))
        
        print("✅ BUSINESS LOGIC: Flujo de negocio end-to-end funcionando")