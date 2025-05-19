from odoo import models, fields, api

class Project(models.Model):
    _name = 'project.management'
    _description = 'Project Management'
    _order = 'date_start asc'

    name = fields.Char(string='Project Name', required=True)
    supervisor_id = fields.Many2one('res.users', string='Assigned Supervisor', required=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date')
    description = fields.Text(string='Description')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        string='State',
        default='draft'
    )
    progress = fields.Float(string='Progress', compute='_compute_progress', store=True)

    @api.depends('task_ids.state')
    def _compute_progress(self):
        for project in self:
            if project.task_ids:
                total_tasks = len(project.task_ids)
                completed_tasks = len(project.task_ids.filtered(lambda t: t.state == 'completed'))
                project.progress = (completed_tasks / total_tasks) * 100
            else:
                project.progress = 0.0

    task_ids = fields.One2many('project.task', 'project_id', string='Tasks')