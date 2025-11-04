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

        # Determine dashboard date range
        if dashboard.date_mode == 'yesterday':
            target_date_start = target_date_end = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        elif dashboard.date_mode == 'custom':
            # dashboard.date_start and date_end are strings in Odoo 8
            target_date_start = dashboard.date_start or date.today().strftime('%Y-%m-%d')
            target_date_end = dashboard.date_end or date.today().strftime('%Y-%m-%d')
        else:
            target_date_start = target_date_end = date.today().strftime('%Y-%m-%d')

        for lst in lists:
            if not lst.display:
                continue

            base_model = lst.model_id.model.replace('.', '_')
            date_field = lst.date_field_name or 'create_date'

            # Find window action
            action = self.env['ir.actions.act_window'].search(
                [('res_model', '=', lst.model_id.model), ('view_type', '=', 'form')],
                limit=1
            )

            # Base query using str.format (Python 2.7 compatible)
            if lst.type == 'money':
                query = "SELECT sum({0}) as field FROM {1}".format(lst.field_id.name, base_model)
            else:
                query = "SELECT count({0}) as field FROM {1}".format(lst.field_id.name, base_model)

            query_action = "SELECT id as id FROM {0}".format(base_model)

            # Filter for non-date conditions
            dynamic_filter = (lst.filter or "").strip()

            # Build WHERE clause
            where_clause_parts = []

            if self.has_active(lst.model_id):
                where_clause_parts.append("{0}.active=true".format(base_model))

            if dynamic_filter:
                where_clause_parts.append(dynamic_filter)

            # Always add dashboard date range on chosen date field
            where_clause_parts.append(
                "{0}.{1}::date BETWEEN '{2}' AND '{3}'".format(base_model, date_field, target_date_start, target_date_end)
            )

            where_clause = " WHERE " + " AND ".join(where_clause_parts)

            # Final queries
            query = query + where_clause
            query_action = query_action + where_clause

            # Execute
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()[0]
            field_value = result['field']

            self.env.cr.execute(query_action)
            result_ids = self.env.cr.dictfetchall()
            res_ids = [res['id'] for res in result_ids]

            last_slices_list.append([
                field_value,
                lst.name or lst.field_id.field_description,
                lst.color,
                lst.icon,
                action.id,
                res_ids,
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
    display_date_mode = fields.Char(string='Date Mode')






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
