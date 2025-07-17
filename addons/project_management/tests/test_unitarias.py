# tests/test_unitarias.py
from odoo.tests.common import TransactionCase
from odoo.tests.common import HttpCase
from odoo.exceptions import UserError

class TestUsuarioUnitario(TransactionCase):
    def test_crear_usuario_valido(self):
        """Prueba unitaria: crear usuario con datos válidos"""
        usuario = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@example.com',
            'email': 'test@example.com'
        })
        self.assertTrue(usuario.id)
        self.assertEqual(usuario.name, 'Test User')




class TestLoginWeb(HttpCase):
    def test_login_usuario_web(self):
        # Crear usuario
        usuario = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@example.com',
            'password': 'test1234'
        })
        
        # Probar login HTTP
        self.authenticate('test@example.com', 'test123')
        response = self.url_open('/web')
        self.assertEqual(response.status_code, 200)





class TestPasswordPolicy(TransactionCase):
    
    def setUp(self):
        super(TestPasswordPolicy, self).setUp()
        self.config_param = self.env['ir.config_parameter'].sudo()
        
        # Limpiar todas las configuraciones antes de cada prueba
        self.config_param.set_param('auth_password_policy.minlength', '0')
        self.config_param.set_param('auth_password_policy.minclasses', '0')
        self.config_param.set_param('auth_password_policy.minwords', '0')
        # Datos de usuario base
        self.user_data = {
            'name': 'Test User',
            'login': 'test@example.com',
            'email': 'test@example.com'
        }
    
    # =============== TESTS DE LONGITUD MÍNIMA ===============
    
    def test_minlength_valid(self): ## Correctamente válidado
        """Prueba contraseña válida con longitud mínima"""
        self.config_param.set_param('auth_password_policy.minlength', '8')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'validpass123'  # 12 caracteres
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)

    def test_minlength_invalid(self): ## correctamente no válidado
        """Prueba contraseña inválida por longitud"""
        self.config_param.set_param('auth_password_policy.minlength', '8')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'short'  # 5 caracteres
        
        with self.assertRaises(UserError) as context:
            self.env['res.users'].create(user_data)
        
        error_message = str(context.exception)
        self.assertIn('at least 8 characters', error_message)
    
    # =============== TESTS DE CLASES DE CARACTERES ===============
    
    def test_minclasses_valid(self):## Correctamente válidado 
        """Prueba contraseña válida con clases de caracteres"""
        self.config_param.set_param('auth_password_policy.minclasses', '3')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'Password123'  # Mayúscula, minúscula, dígito
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)
    
    '''
    2025-07-16 22:44:57,985 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: FAIL: TestPasswordPolicy.test_minclasses_invalid
    Traceback (most recent call last):
    File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 99, in test_minclasses_invalid
        with self.assertRaises(UserError) as context:
    File "/usr/lib/python3.12/contextlib.py", line 144, in __exit__
        next(self.gen)
    File "/usr/lib/python3/dist-packages/odoo/tests/common.py", line 481, in _assertRaises
        with ExitStack() as inner:
    File "/usr/lib/python3.12/contextlib.py", line 610, in __exit__
        raise exc_details[1]
    File "/usr/lib/python3.12/contextlib.py", line 595, in __exit__
        if cb(*exc_details):
        ^^^^^^^^^^^^^^^^
    AssertionError: UserError not raised
    '''
    def test_minclasses_invalid(self):## no validado 
        """Prueba contraseña inválida por clases de caracteres"""
        self.config_param.set_param('auth_password_policy.minclasses', '3')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'password'  # Solo minúsculas
        
        with self.assertRaises(UserError) as context:
            self.env['res.users'].create(user_data)
        
        error_message = str(context.exception)
        self.assertIn('at least 3 different character classes', error_message)
    
    def test_minclasses_with_symbols(self):## Correctamente válidado
        """Prueba contraseña con símbolos"""
        self.config_param.set_param('auth_password_policy.minclasses', '4')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'Password123!'  # Todas las clases
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)
    '''
    2025-07-16 22:44:58,217 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: FAIL: TestPasswordPolicy.test_minclasses_only_two_classes
    Traceback (most recent call last):
    File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 122, in test_minclasses_only_two_classes
        with self.assertRaises(UserError) as context:
    File "/usr/lib/python3.12/contextlib.py", line 144, in __exit__
        next(self.gen)
    File "/usr/lib/python3/dist-packages/odoo/tests/common.py", line 481, in _assertRaises
        with ExitStack() as inner:
    File "/usr/lib/python3.12/contextlib.py", line 610, in __exit__
        raise exc_details[1]
    File "/usr/lib/python3.12/contextlib.py", line 595, in __exit__
        if cb(*exc_details):
        ^^^^^^^^^^^^^^^^
    AssertionError: UserError not raised
    '''
    def test_minclasses_only_two_classes(self): #no valido
        """Prueba contraseña con solo 2 clases cuando se requieren 4"""
        self.config_param.set_param('auth_password_policy.minclasses', '4')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'password123'  # Solo minúsculas y dígitos
        
        with self.assertRaises(UserError) as context:
            self.env['res.users'].create(user_data)
        
        error_message = str(context.exception)
        self.assertIn('at least 4 different character classes', error_message)
    
    # =============== TESTS DE NÚMERO DE PALABRAS ===============
    
    def test_minwords_valid(self):
        """Prueba contraseña válida con número de palabras"""
        self.config_param.set_param('auth_password_policy.minwords', '2')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'my secure password'  # 3 palabras
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)
    '''
        2025-07-16 22:44:59,510 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: FAIL: TestPasswordPolicy.test_minwords_invalid
    Traceback (most recent call last):
    File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 147, in test_minwords_invalid
        with self.assertRaises(UserError) as context:
    File "/usr/lib/python3.12/contextlib.py", line 144, in __exit__
        next(self.gen)
    File "/usr/lib/python3/dist-packages/odoo/tests/common.py", line 481, in _assertRaises
        with ExitStack() as inner:
    File "/usr/lib/python3.12/contextlib.py", line 610, in __exit__
        raise exc_details[1]
    File "/usr/lib/python3.12/contextlib.py", line 595, in __exit__
        if cb(*exc_details):
        ^^^^^^^^^^^^^^^^
    AssertionError: UserError not raised
    '''
    def test_minwords_invalid(self): ## incorrectamente no válidado
        """Prueba contraseña inválida por número de palabras"""
        self.config_param.set_param('auth_password_policy.minwords', '3')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'one word'  # 2 palabras
        
        with self.assertRaises(UserError) as context:
            self.env['res.users'].create(user_data)
        
        error_message = str(context.exception)
        self.assertIn('at least 3 words', error_message)
    '''
    ==============================================================
    2025-07-16 22:44:59,867 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: FAIL: TestPasswordPolicy.test_minwords_single_word
    Traceback (most recent call last):
    File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 160, in test_minwords_single_word
        with self.assertRaises(UserError) as context:
    File "/usr/lib/python3.12/contextlib.py", line 144, in __exit__
        next(self.gen)
    File "/usr/lib/python3/dist-packages/odoo/tests/common.py", line 481, in _assertRaises
        with ExitStack() as inner:
    File "/usr/lib/python3.12/contextlib.py", line 610, in __exit__
        raise exc_details[1]
    File "/usr/lib/python3.12/contextlib.py", line 595, in __exit__
        if cb(*exc_details):
        ^^^^^^^^^^^^^^^^
    AssertionError: UserError not raised
    '''
    def test_minwords_single_word(self):
        """Prueba contraseña de una sola palabra"""
        self.config_param.set_param('auth_password_policy.minwords', '2')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'singleword'  # 1 palabra
        
        with self.assertRaises(UserError) as context:
            self.env['res.users'].create(user_data)
        
        error_message = str(context.exception)
        self.assertIn('at least 2 words', error_message)
    
    # =============== TESTS COMBINADOS ===============
    
    def test_multiple_policies_valid(self): ## correctamente válidado
        """Prueba contraseña válida con múltiples políticas"""
        self.config_param.set_param('auth_password_policy.minlength', '10')
        self.config_param.set_param('auth_password_policy.minclasses', '3')
        self.config_param.set_param('auth_password_policy.minwords', '2')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'My Password123'  # 14 chars, 3 clases, 2 palabras
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)
    '''
    2025-07-16 22:45:00,396 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: FAIL: TestPasswordPolicy.test_multiple_policies_invalid
    Traceback (most recent call last):
    File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 195, in test_multiple_policies_invalid
        self.assertIn('at least 3 different character classes', error_message)
    AssertionError: 'at least 3 different character classes' not found in 'Your password must contain at least 10 characters and only has 5.'
    '''
    def test_multiple_policies_invalid(self):## no válidado
        """Prueba contraseña inválida con múltiples políticas"""
        self.config_param.set_param('auth_password_policy.minlength', '10')
        self.config_param.set_param('auth_password_policy.minclasses', '3')
        self.config_param.set_param('auth_password_policy.minwords', '2')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'short'  # Falla en todas las políticas
        
        with self.assertRaises(UserError) as context:
            self.env['res.users'].create(user_data)
        
        error_message = str(context.exception)
        # Debe contener errores para todas las políticas
        self.assertIn('at least 10 characters', error_message)
        self.assertIn('at least 3 different character classes', error_message)
        self.assertIn('at least 2 words', error_message)
    
    # =============== TESTS DE POLÍTICAS DESHABILITADAS ===============
    
    def test_all_policies_disabled(self):## correctamente válidado
        """Prueba cuando todas las políticas están deshabilitadas"""
        self.config_param.set_param('auth_password_policy.minlength', '0')
        self.config_param.set_param('auth_password_policy.minclasses', '0')
        self.config_param.set_param('auth_password_policy.minwords', '0')
        
        user_data = self.user_data.copy()
        user_data['password'] = 'a'  # Contraseña muy simple
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)
    
    def test_empty_password(self): ##correctamente válidado
        """Prueba contraseña vacía (debe ser ignorada)"""
        self.config_param.set_param('auth_password_policy.minlength', '8')
        
        user_data = self.user_data.copy()
        user_data['password'] = ''
        
        user = self.env['res.users'].create(user_data)
        self.assertTrue(user.id)
    
    # =============== TESTS DE MÉTODO GET_PASSWORD_POLICY ===============
    
    '''2025-07-16 22:44:57,736 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: ERROR: TestPasswordPolicy.test_get_password_policy_all_params
        Traceback (most recent call last):
        File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 233, in test_get_password_policy_all_params
            self.assertEqual(policy['minclasses'], 4)
                            ~~~~~~^^^^^^^^^^^^^^
        KeyError: 'minclasses'''
    def test_get_password_policy_all_params(self): ## test no valido falta correcion
        """Prueba obtener todas las políticas configuradas"""
        self.config_param.set_param('auth_password_policy.minlength', '12')
        self.config_param.set_param('auth_password_policy.minclasses', '4')
        self.config_param.set_param('auth_password_policy.minwords', '3')
        
        policy = self.env['res.users'].get_password_policy()
        
        self.assertEqual(policy['minlength'], 12)
        self.assertEqual(policy['minclasses'], 4)
        self.assertEqual(policy['minwords'], 3)
    ''' 
    2025-07-16 22:44:57,736 1 ERROR postgres odoo.addons.project_management.tests.test_unitarias: ERROR: TestPasswordPolicy.test_get_password_policy_all_params
Traceback (most recent call last):
  File "/mnt/extra-addons/project_management/tests/test_unitarias.py", line 233, in test_get_password_policy_all_params
    self.assertEqual(policy['minclasses'], 4)
                     ~~~~~~^^^^^^^^^^^^^^
KeyError: 'minclasses'
    
    '''
    def test_get_password_policy_defaults(self):
        """Prueba obtener políticas con valores por defecto"""
        # No configurar ningún parámetro
        policy = self.env['res.users'].get_password_policy()
        
        self.assertEqual(policy['minlength'], 0)
        self.assertEqual(policy['minclasses'], 0)
        self.assertEqual(policy['minwords'], 0)


