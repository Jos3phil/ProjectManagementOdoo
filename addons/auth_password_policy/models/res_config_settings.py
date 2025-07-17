from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minlength = fields.Integer(
        "Minimum Password Length", config_parameter="auth_password_policy.minlength", default=0,
        help="Minimum number of characters passwords must contain, set to 0 to disable.")
    minclasses = fields.Integer(
        "Minimum Character Classes", config_parameter="auth_password_policy.minclasses", default=0,
        help="Minimum number of character classes (uppercase, lowercase, digits, symbols). Set to 0 to disable.")

    minwords = fields.Integer(
        "Minimum Number of Words", config_parameter="auth_password_policy.minwords", default=0,
        help="Minimum number of words in the password. Set to 0 to disable.")

    @api.onchange('minlength', 'minclasses', 'minwords')
    def _on_change_policy(self):
        self.minlength = max(0, self.minlength or 0)
        self.minclasses = max(0, self.minclasses or 0)
        self.minwords = max(0, self.minwords or 0)
