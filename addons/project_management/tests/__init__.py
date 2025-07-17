# Solo importar pruebas de Odoo cuando el módulo esté disponible
try:

    from . import test_unitarias
    from . import test_project
    from . import test_task
except ImportError:
    # Odoo no está disponible, las pruebas unitarias puras se ejecutan independientemente
    pass