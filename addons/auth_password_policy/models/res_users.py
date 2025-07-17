# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def get_password_policy(self):
        params = self.env['ir.config_parameter'].sudo()
        return {
            'minlength': int(params.get_param('auth_password_policy.minlength', default=0)),
            'minclasses' : int(params.get_param('auth_password_policy.minclasses', default = 0)),
            'minwords' : int(params.get_param('auth_password_policy.minwords', default = 0))
        }

    def _set_password(self):
        self._check_password_policy(self.mapped('password'))

        super(ResUsers, self)._set_password()

    def _check_password_policy(self, passwords):
        failures = []
        params = self.env['ir.config_parameter'].sudo()

        minlength = int(params.get_param('auth_password_policy.minlength', default=0))
        minclasses = int(params.get_param('auth_password_policy.minclasses', default=0))
        minwords = int(params.get_param('auth_password_policy.minwords', default=0))
        for password in passwords:
            
            if not password:
                continue
            
            # Validar longitud mínima
            if minlength > 0 and len(password) < minlength:
                failures.append(_("Your password must contain at least %(minimal_length)d characters and only has %(current_count)d.", 
                                minimal_length=minlength, current_count=len(password)))
            
            # Validar clases de caracteres
            if minclasses > 0:
                classes = 0
                if re.search(r'[a-z]', password):  # Minúsculas
                    classes += 1
                if re.search(r'[A-Z]', password):  # Mayúsculas
                    classes += 1
                if re.search(r'[0-9]', password):  # Dígitos
                    classes += 1
                if re.search(r'[^a-zA-Z0-9]', password):  # Símbolos
                    classes += 1
                
                if classes < minclasses:
                    password_failures.append(_("Your password must contain at least %(minclasses)d different character classes.", 
                                    minclasses=minclasses))
            
            # Validar número de palabras
            if minwords > 0:
                words = len(password.split())
                if words < minwords:
                    password_failures.append(_("Your password must contain at least %(minwords)d words.", 
                                    minwords=minwords))
            
            # Agregar todos los errores de esta contraseña
            failures.extend(password_failures)

        # Lanzar error solo al final con todos los fallos
        if failures:
            raise UserError('\n\n'.join(failures))