from openerp import models, fields, api
import datetime
from datetime import date, timedelta


class Dashboard(models.Model):
    _name = 'dashboard.dashboard'

    def has_active(self, model):
        for field in model.field_id:
            if field.name == 'active':
                return True
        return False


    def custom_dashboard(self, cr, uid, start_date=None, end_date=None, context=None):
        st_dat = (start_date or date.today()).strftime('%Y-%m-%d 00:00:00')
        end_dat = (end_date or date.today()).strftime('%Y-%m-%d 23:59:59')

        result = {
        }

        opd_q = """
            SELECT 
                COUNT(ot.id) AS ticket_count, 
                SUM(otl.total_amount) AS total_amount_sum 
            FROM opd_ticket ot 
            JOIN opd_ticket_line otl ON otl.opd_ticket_id = ot.id 
            WHERE ot.state = 'confirmed'
            AND ot.create_date >= '%s' 
            AND ot.create_date <= '%s';
        """

        cr.execute(opd_q % (st_dat, end_dat))
        data = cr.fetchone()   # fetch single row (count, sum)

        ticket_count = int(data[0] or 0)
        total_amount = int(data[1] or 0)

        result['opd_income'] = {
            'count': ticket_count,
            'amount': total_amount
        }

# this block is for dental

        opd_dental_q = """
        SELECT 
        COUNT(ot.id) AS dental_opd_count,
        SUM(otl.total_amount) AS dental_opd_amount
        FROM opd_ticket ot
        JOIN opd_ticket_line otl ON otl.opd_ticket_id = ot.id
        WHERE ot.state = 'confirmed'
        AND ot.create_date >= '%s'
        AND ot.create_date <= '%s'
        AND otl.department ILIKE '%%dental%%';
        """

        cr.execute(opd_dental_q % (st_dat, end_dat))
        opd_dental_data = cr.fetchone()

        opd_dent_count = int(opd_dental_data[0] or 0)
        opd_dent_amount = int(opd_dental_data[1] or 0)

        result['dental_opd'] = {
            'count': opd_dent_count,
            'amount': opd_dent_amount
        }


        dental_bill_q = """
            SELECT 
                COUNT(br.id) AS bill_count,
                SUM(br.grand_total) AS total_bill_amount
            FROM bill_register br
            JOIN bill_register_line brl ON brl.bill_register_id = br.id
            WHERE br.state = 'confirmed'
            AND br.create_date >= '%s'
            AND br.create_date <= '%s'
            AND brl.department ILIKE '%%dental%%';
        """

        cr.execute(dental_bill_q % (st_dat, end_dat))
        bill_data = cr.fetchone()

        bill_count = int(bill_data[0] or 0)
        bill_amount = int(bill_data[1] or 0)

        result['dental_income'] = {
            'count': bill_count,
            'amount': bill_amount
        }

    # dental blcok end


    # physiotherapy block 
    
        opd_physio_q = """
        SELECT 
        COUNT(ot.id) AS dental_opd_count,
        SUM(otl.total_amount) AS dental_opd_amount
        FROM opd_ticket ot
        JOIN opd_ticket_line otl ON otl.opd_ticket_id = ot.id
        WHERE ot.state = 'confirmed'
        AND ot.create_date >= '%s'
        AND ot.create_date <= '%s'
        AND otl.department ILIKE '%%physiot%%';
        """

        cr.execute(opd_physio_q % (st_dat, end_dat))
        opd_physio_data = cr.fetchone()

        opd_physio_count = int(opd_physio_data[0] or 0)
        opd_physio_amount = int(opd_physio_data[1] or 0)

        result['physiotherpay_opd'] = {
            'count': opd_dent_count,
            'amount': opd_dent_amount
        }


        physio_bill_q = """
            SELECT 
                COUNT(br.id) AS bill_count,
                SUM(br.grand_total) AS total_bill_amount
            FROM bill_register br
            JOIN bill_register_line brl ON brl.bill_register_id = br.id
            WHERE br.state = 'confirmed'
            AND br.create_date >= '%s'
            AND br.create_date <= '%s'
            AND brl.department ILIKE '%%physiot%%';
        """

        cr.execute(physio_bill_q % (st_dat, end_dat))
        physio_data = cr.fetchone()

        physiotherapy_bill_count = int(physio_data[0] or 0)
        physiotherapy_bill_amount = int(physio_data[1] or 0)

        result['physiotherapy_bill'] = {
            'count': bill_count,
            'amount': bill_amount
        }

    # end physiotherpay 

        return result

    
    # def cash_collection(self,cr,uid,context=None):

    def _compute_field_list(self):
        dashboard = self.env['dashboard.settings'].search([], limit=1, order='id desc')
        lists = dashboard.line_ids
        last_slices_list = []

        # self.custom_dashboard()

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
