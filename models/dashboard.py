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



    def custom_dashboard(self, start_date=None, end_date=None):
        if start_date:
            formatted_start_date = datetime.datetime.strptime(start_date.split("T")[0], "%Y-%m-%d")
        if end_date:
            formatted_end_date = datetime.datetime.strptime(end_date.split("T")[0], "%Y-%m-%d")
       

        # fallback dates
        st = (formatted_start_date or date.today()).strftime('%Y-%m-%d 00:00:00')
        en = (formatted_end_date or date.today()).strftime('%Y-%m-%d 23:59:59')

        result = {}

        self.env.cr.execute("""
            SELECT COUNT(ot.id), SUM(otl.total_amount)
            FROM opd_ticket ot
            JOIN opd_ticket_line otl ON otl.opd_ticket_id = ot.id
            WHERE ot.state='confirmed'
            AND ot.create_date >= %s AND ot.create_date <= %s
        """, (st, en))
        c, a = self.env.cr.fetchone()
        result['opd_income'] = {'count': c or 0, 'amount': a or 0}


        # Dental OPD
        self.env.cr.execute("""
            SELECT COUNT(ot.id), SUM(otl.total_amount)
            FROM opd_ticket ot 
            JOIN opd_ticket_line otl ON otl.opd_ticket_id = ot.id
            WHERE ot.state='confirmed'
            AND ot.create_date >= %s AND ot.create_date <= %s
            AND otl.department ILIKE 'dental'
        """, (st, en))
        c, a = self.env.cr.fetchone()
        result['dental_opd'] = {'count': c or 0, 'amount': a or 0}


        # Dental Bill
        self.env.cr.execute("""
            SELECT COUNT(br.id), SUM(br.grand_total),SUM(mr.amount) AS total_paid_amount
            FROM bill_register br
            JOIN bill_register_line brl ON brl.bill_register_id = br.id
            LEFT JOIN leih_money_receipt mr ON mr.bill_id = br.id AND mr.state = 'confirm'
            WHERE br.state='confirmed'
            AND br.create_date >= %s AND br.create_date <= %s
            AND brl.department ILIKE 'dental'
        """, (st, en))
        count, total, paid = self.env.cr.fetchone()
        result['dental_income'] = {
            'count': count or 0,
            'amount': total or 0,
            'paid': paid or 0,
        }


        self.env.cr.execute("""
        SELECT 
        COUNT(ot.id) AS ticket_count, 
        SUM(otl.total_amount) AS total_amount
        FROM opd_ticket ot
        JOIN opd_ticket_line otl ON otl.opd_ticket_id = ot.id
        WHERE ot.state = 'confirmed'
        AND ot.date >= %s AND ot.date <= %s
        AND otl.department ILIKE '%%physiotherapy%%'
        """, (st, en))

        count, amount = self.env.cr.fetchone()

        result['physiotherapy_opd'] = {
        'count': count or 0,
        'amount': amount or 0,
        }



        # Physiotherapy bill
        self.env.cr.execute("""
        SELECT 
        COUNT(DISTINCT br.id) AS bill_count,
        SUM(br.grand_total) AS total_bill_amount,
        SUM(mr.amount) AS total_paid_amount
        FROM bill_register br
        JOIN bill_register_line brl ON brl.bill_register_id = br.id
        LEFT JOIN leih_money_receipt mr ON mr.bill_id = br.id AND mr.state = 'confirm'
        WHERE br.state = 'confirmed'
        AND br.create_date >= %s AND br.create_date <= %s
        AND brl.department ILIKE 'Physiotherapy'
        """, (st, en))

        count, total, paid = self.env.cr.fetchone()

        result['physiotherapy_bill'] = {
            'count': count or 0,
            'amount': total or 0,
            'paid': paid or 0,
        }

        #admission income
        self.env.cr.execute("""
        SELECT
            COUNT(DISTINCT adm.id) AS admission_count,
            SUM(adm.grand_total) AS total_admission_amount,
            SUM(mr.amount) AS total_paid_amount
        FROM leih_admission adm
        LEFT JOIN leih_money_receipt mr 
            ON mr.admission_id = adm.id 
            AND mr.state = 'confirm'
        WHERE adm.state = 'activated'
        AND adm.date >= %s AND adm.date <= %s
        """, (st, en))

        count, total, paid = self.env.cr.fetchone()

        result['admission'] = {
            'count': count or 0,
            'amount': total or 0,
            'paid': paid or 0,
        }

        #Number of Surgery

        self.env.cr.execute("""
        SELECT 
        COUNT(*) AS surgery_count
        FROM leih_admission
        WHERE operation_date IS NOT NULL
        AND operation_date >= %s AND operation_date <= %s
        """, (st, en))

        (surgery_count,) = self.env.cr.fetchone()

        result['surgery'] = {
            'count': surgery_count or 0,
        }



        #optics income
        self.env.cr.execute("""
        SELECT
        COUNT(DISTINCT os.id) AS sale_count,
        SUM(os.total) AS total_amount,
        SUM(mr.amount) AS total_paid
        FROM optics_sale os
        LEFT JOIN leih_money_receipt mr
        ON mr.optics_sale_id = os.id
        AND mr.state = 'confirm'
        WHERE os.date >= %s AND os.date <= %s
        """, (st, en))

        count, amount, paid = self.env.cr.fetchone()

        result['optics_income'] = {
            'count': count or 0,
            'amount': amount or 0,
            'paid': paid or 0,
        }

        # Investigation Income
        self.env.cr.execute("""
        SELECT 
        COUNT(DISTINCT br.id) AS bill_count,
        SUM(br.grand_total) AS total_amount,
        SUM(mr.amount) AS total_paid
        FROM bill_register br
        JOIN bill_register_line brl 
        ON brl.bill_register_id = br.id
        LEFT JOIN leih_money_receipt mr 
        ON mr.bill_id = br.id 
        AND mr.state = 'confirm'
        WHERE br.state = 'confirmed'
        AND br.create_date >= %s 
        AND br.create_date <= %s
        AND brl.department NOT ILIKE 'dental'
        AND brl.department NOT ILIKE 'physiot'
        """, (st, en))

        count, total, paid = self.env.cr.fetchone()

        result['investigation_income'] = {
            'count': count or 0,
            'amount': total or 0,
            'paid': paid or 0,
        }


        #Pharmacy Income
        self.env.cr.execute("""
        SELECT
        COUNT(DISTINCT po.id) AS order_count,
        SUM(pol.price_subtotal) AS total_subtotal
        FROM pos_order po
        JOIN pos_order_line pol 
            ON pol.order_id = po.id
        WHERE po.date_order >= %s 
        AND po.date_order <= %s
        """, (st, en))

        order_count, subtotal = self.env.cr.fetchone()

        result['pos_income'] = {
        'count': order_count or 0,
        'subtotal': subtotal or 0,
        }

  

        #cash collection

        self.env.cr.execute("""
        SELECT
        COUNT(mr.id) AS receipt_count,
        SUM(mr.amount) AS total_collected_amount
        FROM leih_money_receipt mr
        WHERE mr.state = 'confirm'
        AND mr.create_date >= %s AND mr.create_date <= %s
        """, (st, en))

        count, total = self.env.cr.fetchone()

        result['money_receipt'] = {
        'count': count or 0,
        'amount': total or 0,
        }

        #Discount
        self.env.cr.execute("""
        SELECT
        COUNT(d.id) AS discount_count,
        SUM(d.total_discount) AS total_discount_amount
        FROM discount d
        WHERE d.state = 'approve'
        AND d.date >= %s AND d.date <= %s
        """, (st, en))

        count, total_discount = self.env.cr.fetchone()

        result['discount'] = {
        'count': count or 0,
        'total_discount': total_discount or 0,
        }
        # result['eye_doctor']=self.doctor_income(start_date,end_date)
        # result['dental_doctor']=self.doctor_dental_income(start_date,end_date)
        # result['physiotherapis']=self.physiotherapist_income(start_date,end_date)
        merged_dict = result.copy()  # start with your main dict
        merged_dict.update(self.doctor_income(start_date, end_date))
        merged_dict.update(self.doctor_dental_income(start_date, end_date))
        merged_dict.update(self.physiotherapist_income(start_date, end_date))
        return merged_dict




        #Discount

    @api.model
    def doctor_income(self, start_date=None, end_date=None):
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
       

        # fallback dates
        st = (start_date or date.today()).strftime('%Y-%m-%d 00:00:00')
        en = (end_date or date.today()).strftime('%Y-%m-%d 23:59:59')

        result = {}
        self.env.cr.execute("""
        SELECT
        dp.doctor_id,
        dp.name AS doctor_name,
        SUM(total_income) AS combined_income,
        SUM(total_count) AS combined_count
        FROM (
        SELECT
            la.ref_doctors AS doctor_id,
            SUM(la.grand_total) AS total_income,
            COUNT(la.id) AS total_count
        FROM leih_admission la
        WHERE la.state = 'activated'
        AND la.date >= %s AND la.date <= %s
        GROUP BY la.ref_doctors

        UNION ALL
        SELECT
            br.ref_doctors AS doctor_id,
            SUM(br.grand_total) AS total_income,
            COUNT(br.id) AS total_count
        FROM bill_register br
        JOIN bill_register_line brl
            ON brl.bill_register_id = br.id
        JOIN examination_entry ee
            ON ee.id = brl.name
        JOIN diagnosis_department dd
            ON dd.id = ee.department
        WHERE br.state = 'confirmed'
        AND br.ref_doctors IS NOT NULL
        AND br.create_date >= %s AND br.create_date <= %s
        AND dd.name ILIKE ANY (ARRAY[
            'Retinal Procedure',
            'minor-ot',
            'retinal surgery',
            'other surgery'
        ])
        GROUP BY br.ref_doctors
        ) AS combined

        JOIN doctors_profile dp
        ON dp.id = combined.doctor_id

        GROUP BY dp.doctor_id, dp.name
        ORDER BY combined_income DESC
        """, (st, en, st, en))

        rows = self.env.cr.fetchall()

        result['doctor_total_income'] = [
            {
                'doctor_id': r[0],
                'doctor_name': r[1],
                'income': r[2] or 0,
                'count': r[3] or 0,
            }
            for r in rows
        ]

        return result


    

    @api.model
    def doctor_dental_income(self, start_date=None, end_date=None):
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        st = (start_date or date.today()).strftime('%Y-%m-%d 00:00:00')
        en = (end_date or date.today()).strftime('%Y-%m-%d 23:59:59')

        dental_pattern = '%dental%'

        query = """
            SELECT
                COALESCE(dp.id, 0) AS doctor_id,
                COALESCE(dp.name, 'Undefined') AS doctor_name,
                SUM(br.grand_total) AS income,
                COUNT(DISTINCT br.id) AS bill_count
            FROM bill_register br
            JOIN bill_register_line brl
                ON brl.bill_register_id = br.id
            JOIN examination_entry ee
                ON ee.id = brl.name
            JOIN diagnosis_department dd
                ON dd.id = ee.department
            LEFT JOIN doctors_profile dp
                ON dp.id = br.ref_doctors

            WHERE br.state = 'confirmed'
            AND br.create_date >= %s
            AND br.create_date <= %s
            AND dd.name ILIKE %s

            GROUP BY dp.id, dp.name
            ORDER BY income DESC
        """

        self.env.cr.execute(query, (st, en,dental_pattern))
        rows = self.env.cr.fetchall()

        return {
            'dental_doctor_income': [
                {
                    'doctor_id': r[0],
                    'doctor_name': r[1],
                    'income': r[2] or 0,
                    'count': int(r[3] or 0),
                }
                for r in rows
            ]
        
        }



    @api.model
    def physiotherapist_income(self, start_date=None, end_date=None):
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # Fallbacks
        st = (start_date or date.today()).strftime('%Y-%m-%d 00:00:00')
        en = (end_date or date.today()).strftime('%Y-%m-%d 23:59:59')
        physio_pattern = '%physioth%'

        query = """
            SELECT
                COALESCE(dp.id, 0) AS doctor_id,
                COALESCE(dp.name, 'Undefined') AS doctor_name,
                SUM(br.grand_total) AS income,
                COUNT(DISTINCT br.id) AS bill_count
            FROM bill_register br
            JOIN bill_register_line brl
                ON brl.bill_register_id = br.id
            JOIN examination_entry ee
                ON ee.id = brl.name
            JOIN diagnosis_department dd
                ON dd.id = ee.department
            LEFT JOIN doctors_profile dp
                ON dp.id = br.ref_doctors

            WHERE br.state = 'confirmed'
            AND br.create_date >= %s
            AND br.create_date <= %s
            AND dd.name ILIKE %s

            GROUP BY dp.id, dp.name
            ORDER BY income DESC
        """

        self.env.cr.execute(query, (st, en,physio_pattern))
        rows = self.env.cr.fetchall()

        # import pdb;pdb.set_trace()

        return {
            'physiotherapist_income': [
                {
                    'doctor_id': r[0],
                    'doctor_name': r[1],
                    'income': r[2] or 0,
                    'count': r[3] or 0,
                }
                for r in rows
            ]
        }









    
    # def cash_collection(self,cr,uid,context=None):

    def _compute_field_list(self):
        dashboard = self.env['dashboard.settings'].search([], limit=1, order='id desc')
        lists = dashboard.line_ids
        last_slices_list = []

        # self.custom_dashboard()
        # eye_doctor_income=self.doctor_income()
        # dental_income=self.doctor_dental_income()
        # therapy_income=self.physiotherapist_income()
        # import pdb;pdb.set_trace()

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
