# Solo importar pruebas de Odoo cuando el módulo esté disponible
try:
    
    from . import test_integracion
    
except ImportError:
    # Odoo no está disponible, las pruebas unitarias puras se ejecutan independientemente
    pass