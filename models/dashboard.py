from openerp import models, fields, api
import datetime
from datetime import date


class Dashboard(models.Model):
    _name = 'dashboard.dashboard'

    def has_active(self, model):
        for field in model.field_id:
            if field.name == 'active':
                return True
        return False

    def _compute_field_list(self):
        dashboard = self.env['dashboard.settings'].search([], limit=1, order='id desc')
        lists = dashboard.line_ids
        last_slices_list = []
        today = date.today().strftime("'%Y-%m-%d'")  # e.g., '2025-10-17'

        for list in lists:
            if not list.display:
                continue

            # Base model table name
            base_model = list.model_id.model.replace('.', '_')

            # Find window action
            action = self.env['ir.actions.act_window'].search(
                [('res_model', '=', list.model_id.model), ('view_type', '=', 'form')], limit=1
            )

            # Base queries
            if list.type == 'money':
                requete = "SELECT sum({0}) as field FROM {1}".format(list.field_id.name, base_model)
            else:
                requete = "SELECT count({0}) as field FROM {1}".format(list.field_id.name, base_model)

            requete_action = "SELECT id as id FROM {0}".format(base_model)

            # Replace placeholder {today} with actual date string
            dynamic_filter = list.filter.replace("{today}", today) if list.filter else False

            # --- Detect relation in filter (e.g., bill_register_line.department ...)
            join_clause = ""
            if dynamic_filter and '.' in dynamic_filter:
                first_part = dynamic_filter.split('.')[0]  # e.g., bill_register_line
                # assume relation field is <base_model>_id
                join_clause = " JOIN {0} ON {0}.{1}_id = {2}.id".format(
                    first_part, base_model, base_model
                )
                # remove prefix for WHERE part
                dynamic_filter = dynamic_filter.replace(first_part + ".", "")

            # --- Build WHERE clause
            where_clause = ""
            if self.has_active(list.model_id) and dynamic_filter:
                where_clause = " WHERE {0}.active=true AND {1}".format(base_model, dynamic_filter)
            elif self.has_active(list.model_id):
                where_clause = " WHERE {0}.active=true".format(base_model)
            elif dynamic_filter:
                where_clause = " WHERE {0}".format(dynamic_filter)

            # --- Combine query
            requete = requete + join_clause + where_clause
            requete_action = requete_action + join_clause + where_clause


            # Execute SQL
            print('----------------------------requete', requete)
            self.env.cr.execute(requete.replace('"', "'"))
            result = self.env.cr.dictfetchall()[0]
            field = result['field']
        

            self.env.cr.execute(requete_action.replace('"', "'"))
            result_ids = self.env.cr.dictfetchall()
            res_ids = [res['id'] for res in result_ids]

            last_slices_list.append([
                field,
                list.name or list.field_id.field_description,
                list.color,
                list.icon,
                action.id,
                res_ids
            ])

        return last_slices_list



    def _get_default_chart(self):
        chart_list = []
        dashboard = self.env['dashboard.settings'].search([], limit=1, order='id desc')
        chart_ids = self.env['dashboard.settings.chart'].search([('dashboard_id', '=', dashboard.id)], order='sequence')
        for list in chart_ids:
            if list.display:
                if list.display_type == 'area':
                    chart_list.append([list.id, list.name, 1])
                else:
                    chart_list.append([list.id, list.name, 2])
        return chart_list

    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True, string="Currency")
    field_list = fields.Selection(_compute_field_list, string='Slices names')
    chart_list = fields.Selection(_get_default_chart, string='Charts')

    @api.multi
    def action_setting(self):
        action = self.env.ref('dashboard.action_dashboard_config').read()[0]
        setting = self.env['dashboard.settings'].search([], limit=1, order='id desc').id
        action['views'] = [(self.env.ref('dashboard.dashboard_config_settings').id, 'form')]
        action['res_id'] = setting
        return action

    @api.multi
    def view_details(self):
        action = self.env['ir.actions.act_window'].search([('id', '=', self.env.context['action_id'])], limit=1)
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_mode': 'tree',
            'target': action.target,
            'domain': [('id', 'in', self.env.context['active_ids'])],
            'context': {},
            'res_model': action.res_model,
        }
        return result
