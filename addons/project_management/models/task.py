from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Task(models.Model):
    _name = 'project.task'
    _description = 'Task'
    _order = 'date_start asc'

    name = fields.Char(string='Task Name', required=True)
    project_id = fields.Many2one('project.management', string='Associated Project', required=True)
    executor_id = fields.Many2one('res.users', string='Assigned Executor', required=True)
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    description = fields.Text(string='Description')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        string='State',
        default='draft',
        required=True
    )

    @api.constrains('date_end')
    def _check_end_date(self):
        for task in self:
            if task.date_end and task.date_end < task.date_start:
                raise ValidationError("End date cannot be earlier than start date.")

    def action_start(self):
        self.state = 'in_progress'

    def action_complete(self):
        self.state = 'completed'

    def action_cancel(self):
        self.state = 'cancelled'