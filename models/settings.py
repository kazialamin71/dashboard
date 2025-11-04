from openerp import models, fields, api

class DashboardSettings(models.Model):
    _name = 'dashboard.settings'
    
    
    def get_default_chart_model(self):
        return self.search([],limit=1,order='id desc').chart_model_id.id
    def get_default_chart_measure_field(self):
        return self.search([],limit=1,order='id desc').chart_measure_field_id.id
    def get_default_chart_date_field(self):
        return self.search([],limit=1,order='id desc').chart_date_field_id.id
    
    def get_default_lines(self):
        return self.search([],limit=1,order='id desc').line_ids.ids
    
    def get_default_chart(self):
        return self.search([],limit=1,order='id desc').chart_ids.ids
    
    
    name=fields.Char('Name',default="Setting")
    date_mode = fields.Selection([
        ('today', 'Today'),
        ('yesterday', 'Yesterday'),
        ('custom', 'Custom'),
    ], string='Date Mode', default='today', help="Select which date to use for dashboard filters.")
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    provider_latitude=fields.Char('latitude')
    provider_longitude=fields.Char('ongitude')
    map=fields.Char('ongitude')
    line_ids=fields.One2many('dashboard.settings.line','dashboard_id','Fields',default=get_default_lines)
    chart_ids=fields.One2many('dashboard.settings.chart','dashboard_id','Charts',default=get_default_chart)


    @api.onchange('date_mode', 'date_start', 'date_end')
    def onchange_date_mode(self):
        if not self.date_mode:
            return

        dashboards = self.env['dashboard.dashboard'].search([])  # adjust domain if needed
        value = ''

        if self.date_mode == 'today':
            value = 'Showing Data for: Today'
        elif self.date_mode == 'yesterday':
            value = 'Showing Data for: Yesterday'
        elif self.date_mode == 'custom':
            # Safely handle both date objects and string dates
            def format_date(d):
                if not d:
                    return ''
                if isinstance(d, basestring):  # for Odoo 8 (Python 2)
                    try:
                        d = datetime.strptime(d, '%Y-%m-%d')
                    except Exception:
                        return d
                return d.strftime('%d-%b-%Y')

            start_str = format_date(self.date_start)
            end_str = format_date(self.date_end)

            if start_str and end_str:
                value = 'Showing Data for: {} to {}'.format(start_str, end_str)
            elif start_str:
                value = 'Showing Data from: {}'.format(start_str)
            else:
                value = 'Showing Data for: Custom Range'

        dashboards.write({'display_date_mode': value})

    

class DashboardSettingsLine(models.Model):
    _name = 'dashboard.settings.line'
    
    name=fields.Char('Name')
    model_id = fields.Many2one('ir.model','Model')
    field_id = fields.Many2one('ir.model.fields','Field')
    color=fields.Selection([('red','Red'),('green','Green'),('primary','Primary'),('yellow','Yellow')],string='Color')
    icon=fields.Char('Icon')
    filter=fields.Char('Filter')
    date_field_name = fields.Char('Date Field', help="Name of the date field to use for this card, e.g., create_date or operation_date")
    type=fields.Selection([('money','Money'),('qty','Quantity')],string='Type')
    dashboard_id = fields.Many2one('dashboard.settings','Setting')
    display=fields.Boolean('Show/hide',default=True)
    

class DashboardSettingschart(models.Model):
    _name = 'dashboard.settings.chart'
    
    name=fields.Char('Name')
    sequence=fields.Integer('Sequence',default=1)
    display_type=fields.Selection([('area','Area'),('bar','Bar')],string='Display Type')
    chart_model_id = fields.Many2one('ir.model','Chart Model')
    chart_measure_field_id = fields.Many2one('ir.model.fields','Chart measure Field')
    chart_date_field_id = fields.Many2one('ir.model.fields','Chart date Field')
    filter=fields.Char('Filter')
    type=fields.Selection([('money','Money'),('qty','Quantity')],string='Type')
    dashboard_id = fields.Many2one('dashboard.settings','Setting')
    display=fields.Boolean('Show/hide',default=True)
    

