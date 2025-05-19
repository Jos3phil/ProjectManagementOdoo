from odoo import models, fields, api

class ProjectRole(models.Model):
    _name = 'project.role'
    _description = 'User Role for Project Management'

    name = fields.Char(string='Role Name', required=True)
    description = fields.Text(string='Description', help='Description of the role and its responsibilities')
    permissions = fields.Many2many('ir.model.access', string='Permissions')
    
    # Relación con usuarios
    user_ids = fields.Many2many(
        'res.users',
        string='Users',
        help='Users assigned to this role'
    )

    @api.model
    def create(self, vals):
        """Sobreescribe el método create para asignar permisos cuando se crea un rol."""
        role = super(ProjectRole, self).create(vals)
        return role

    def assign_role_to_user(self, user_id):
        """Assign this role to a user."""
        self.write({'user_ids': [(4, user_id)]})
        return True