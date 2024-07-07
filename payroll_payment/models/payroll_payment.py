from odoo import _, api, fields, models
import io
import xlsxwriter
import base64
from odoo.exceptions import ValidationError
class PayrollPayment(models.Model):
    _name = 'payroll.payment'
    _description = 'Payroll Payment'
    
    name = fields.Char(string='Código', required=True, default=lambda self: _('New'), readonly=True)
    date = fields.Date('Fecha')
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('send', 'Enviada'), 
        ('approved', 'Aprobado'), 
        ('generation_payroll', 'Generación de nómina'), 
        ('done', 'Procesado')
        ], string='Estado', default='draft')
    payroll_payment_type_id = fields.Many2one('payroll.payment.type', string='Tipo de nómina')
    number_of_invoices = fields.Integer('Cantidad de facturas', compute='_compute_number_of_invoices')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Banco')
    # move_ids = fields.One2many('account.move', 'payroll_payment_id', string='Facturas')
    line_ids = fields.One2many('payroll.payment.line', 'payroll_payment_id', string='Facturas')
    budget = fields.Monetary(string='Presupuesto', currency_field='currency_id')
    amount_total =  fields.Monetary(string='Total', currency_field='currency_id', compute='_compute_amount_total')
    payroll_xlsx = fields.Binary(string='Nómina XLSX')
    payroll_xlsx_filename = fields.Char(string='Nombre del archivo XLSX')
    lines_count = fields.Integer(compute='_compute_lines_count', string='Numero de factura')
    move_id = fields.Many2one('account.move', string='Apunte de Contable')
    observations = fields.Text('Observaciones')
    payroll_name = fields.Char('Nombre de la nómina')
    is_remuneration = fields.Boolean(string='Es Remuneración', related='payroll_payment_type_id.is_remuneration')
    mp_flujo_id = fields.Many2one(comodel_name="mp.flujo", domain="[('grupo_flujo_ids', 'in', mp_grupo_flujo_id)]")
    mp_grupo_flujo_ids = fields.Many2many(related="mp_flujo_id.grupo_flujo_ids")
    mp_grupo_flujo_id = fields.Many2one(comodel_name="mp.grupo.flujo", domain="[]")
    
    def assign_grupo_flujo_and_flujo(self):
        for line in self.line_ids:
            if not line.mp_flujo_id or not line.mp_grupo_flujo_id:
                line.mp_grupo_flujo_id = self.mp_grupo_flujo_id
                line.mp_flujo_id = self.mp_flujo_id
    
    @api.onchange("mp_grupo_flujo_id")
    def _onchange_mp_flujo_id(self):
        for register_id in self:
            register_id.mp_flujo_id = self.env['mp.flujo']
    
    @api.depends('line_ids')
    def _compute_lines_count(self):
        for record in self:
            record.lines_count = len(record.line_ids)
    
    @api.depends('line_ids', 'line_ids.amount_total')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(record.line_ids.mapped('amount_total'))
    
    @api.depends('line_ids')
    def _compute_number_of_invoices(self):
        for record in self:
            record.number_of_invoices = len(record.line_ids)
            
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payroll.payment') or _('New')
        result = super(PayrollPayment, self).create(vals)
        return result

    def convert_to_send(self):
        if self.amount_total > self.budget:
            raise ValidationError(_('El monto total de las facturas es mayor al presupuesto.'))
        if not self.line_ids:
            raise ValidationError(_('Debe seleccionar al menos una factura.'))
        if self.line_ids and not all(self.line_ids.mapped(lambda r: bool(r.mp_flujo_id) and bool(r.mp_grupo_flujo_id))):
            raise ValidationError(_('Debe seleccionar un grupo y flujo para todas las facturas.'))
        if self.line_ids and any(self.line_ids.mapped(lambda r: r.move_id.pending_payment_equal_move())):
            raise ValidationError(_('Al menos una factura tiene débito pendiente.'))
        if self.line_ids and all(self.line_ids.mapped(lambda r: bool(r.move_id.mp_flujo_id) and bool(r.move_id.mp_grupo_flujo_id) and not r.move_id.pending_payment_equal_move())) and self.amount_total <= self.budget:
            self.state = 'send'

    def format_template_xlsx_bci(self, workbook):
        worksheet = workbook.add_worksheet('Nómina')
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})
        # Write some data headers.
        # worksheet.write('A1', 'Nº Cuenta de Cargo', bold)
        # worksheet.write('B1', 'Nº Cuenta de Destino', bold)
        # worksheet.write('C1', 'Banco Destino', bold)
        # worksheet.write('D1', 'Rut Benefeciario', bold)
        # worksheet.write('E1', 'Dig Verif. Benefeciario', bold)
        # worksheet.write('F1', 'Nombre Benefeciario', bold)
        # worksheet.write('G1', 'Monto Transferencia', bold)
        # worksheet.write('H1', 'Nº Factura Boleta', bold)
        # worksheet.write('I1', 'Nº Orden de Compra', bold)
        # worksheet.write('J1', 'Tipo de pago', bold)
        # worksheet.write('K1', 'Mensaje Destinatario', bold)
        # worksheet.write('L1', 'Email Destinatario', bold)
        # worksheet.write('M1', 'Cuenta Destino inscrita como', bold)
        worksheet.write('A1', 'Unidad (Desagrupar)', bold)
        worksheet.write('B1', 'RUT', bold)
        worksheet.write('C1', 'Nombre Beneficiario', bold)
        worksheet.write('D1', 'FP', bold)
        worksheet.write('E1', 'BCO', bold)
        worksheet.write('F1', 'Nº Cuenta Cte', bold)
        worksheet.write('G1', 'Nº Documento', bold)
        worksheet.write('H1', 'Monto a agar', bold)
        worksheet.write('I1', 'Of BCI', bold)
        worksheet.write('J1', 'Fecha', bold)
        worksheet.write('K1', 'Rut retirado', bold)
        worksheet.write('L1', 'Ap. paterno', bold)
        worksheet.write('M1', 'Ap. materno', bold)
        worksheet.write('N1', 'Nombre', bold)
        worksheet.write('O1', 'Tipo', bold)
        worksheet.write('P1', 'Glosa', bold)
        worksheet.write('Q1', 'Email', bold)
        worksheet.write('R1', 'Nº Documento Relacionado', bold)
        
        # Start from the first cell below the headers.
        row = 1
        col = 0
        # Iterate over the data and write it out row by row.
        for line in self.line_ids:
            # worksheet.write(row, col, self.partner_bank_id.acc_number or '')
            # worksheet.write(row, col + 1, line.move_id.partner_bank_id.acc_number or '')
            # worksheet.write(row, col + 2, line.move_id.partner_bank_id.bank_id.payroll_code or '')
            # worksheet.write(row, col + 3, line.move_id.partner_id.vat or '')
            # worksheet.write(row, col + 4, line.move_id.partner_id.vat and line.move_id.partner_id.vat[-1] or '')
            # worksheet.write(row, col + 5, line.move_id.partner_id.name or '')
            # worksheet.write(row, col + 6, line.amount_total)
            # worksheet.write(row, col + 7, line.move_id.name or '')
            # worksheet.write(row, col + 8, line.move_id.ref or '')
            # worksheet.write(row, col + 9, 'OTRO *')
            # worksheet.write(row, col + 10, 'PAGO FINIQUITO *')
            # worksheet.write(row, col + 11, line.move_id.partner_id.email or '')
            # worksheet.write(row, col + 12, line.move_id.partner_id.name or '')
            worksheet.write(row, col, '')
            worksheet.write(row, col + 1, line.move_id.partner_id.vat.split('-')[0] if line.move_id.partner_id.vat and '-' in line.move_id.partner_id.vat else '')
            worksheet.write(row, col + 2, line.move_id.partner_id.name or '')
            worksheet.write(row, col + 3, 'OTC')
            worksheet.write(row, col + 4, '012')
            worksheet.write(row, col + 5, line.move_id.partner_bank_id.acc_number or '')
            worksheet.write(row, col + 6, '1')
            worksheet.write(row, col + 7, line.move_id.amount_total or 0)
            worksheet.write(row, col + 8, '')
            worksheet.write(row, col + 9, line.move_id.date)
            worksheet.write(row, col + 10, '')
            worksheet.write(row, col + 11, '')
            worksheet.write(row, col + 12, '')
            worksheet.write(row, col + 13, '')
            worksheet.write(row, col + 14, 'ABO')
            worksheet.write(row, col + 15, 'DEVOLUCION MUNDO PACIFICO')
            worksheet.write(row, col + 16, line.move_id.partner_id.email or '')
            worksheet.write(row, col + 17, '')
            row += 1
        workbook.close()
        
    def format_template_xlsx_itau(self, workbook):
        worksheet = workbook.add_worksheet('Nómina')
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})
        # Write some data headers.
        worksheet.write('A3', 'Rut Empresa', bold)
        worksheet.write('A4', 'Cantidad de Pagos', bold)
        worksheet.write('A5', 'Monto Total de Pagos', bold)
        worksheet.write('A6', 'Tipo de Producto', bold)
        worksheet.write('A7', 'Tipo de Servicio', bold)
        worksheet.write('A8', 'Nº Cuenta Cargo', bold)
        worksheet.write('A9', 'Glosa Cartola Origen', bold)
        worksheet.write('A10', 'Glosa Cartola Destino', bold)
        ############
        worksheet.write('B3', self.env.company.vat or '')
        worksheet.write('B4', len(self.line_ids))
        worksheet.write('B5', self.amount_total)
        worksheet.write('B6', 'Proveedores')
        worksheet.write('B7', 'PAGO_DE_PROVEEDORES')
        worksheet.write('B8', self.partner_bank_id.acc_number or '')
        worksheet.write('B9', 'TRASPASO A BCI')
        worksheet.write('B10', 'TRASPASO DESDE ITAU')
        ############
        worksheet.write('A12', 'Rut Beneficiario', bold)
        worksheet.write('B12', 'Nombre Benefeciario', bold)
        worksheet.write('C12', 'Monto', bold)
        worksheet.write('D12', 'Medio de Pago', bold)
        worksheet.write('E12', 'Código Banco', bold)
        worksheet.write('F12', 'Tipo de Cuenta', bold)
        worksheet.write('G12', 'Número de Cuenta', bold)
        worksheet.write('H12', 'Email', bold)
        worksheet.write('I12', 'Referencia Cliente', bold)
        worksheet.write('J12', 'Glosa Cartola Origen', bold)
        worksheet.write('K12', 'Glosa Cartola Destino', bold)
        worksheet.write('L12', 'Detalle de Pago', bold)
        # Start from the first cell below the headers.
        row = 12
        col = 0
        # Iterate over the data and write it out row by row.
        for line in self.line_ids:
            worksheet.write(row, col, line.move_id.partner_id.vat or '')
            worksheet.write(row, col + 1, line.move_id.partner_id.name or '')
            worksheet.write(row, col + 2, line.amount_total)
            worksheet.write(row, col + 3, 'Abono en cuenta *')
            worksheet.write(row, col + 4, line.move_id.partner_bank_id.bank_id.payroll_code or '')
            worksheet.write(row, col + 5, 'Cuenta corriente *')
            worksheet.write(row, col + 6, line.move_id.partner_bank_id.acc_number or '')
            worksheet.write(row, col + 7, line.move_id.partner_id.email or '')
            worksheet.write(row, col + 8, 'TRASPASO DESDE ITAU A BCI')
            worksheet.write(row, col + 9, 'TRASPASO A BCI')
            worksheet.write(row, col + 10, 'TRASPASO ENTRE CUENTAS ITAU A BCI')
            row += 1
        workbook.close()
        
    def format_template_xlsx_scotiabank(self, workbook):
        worksheet = workbook.add_worksheet('Nómina')
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': True})
        # Write some data headers.
        worksheet.write('A1', 'Rut Proveedor Beneficiario', bold)
        worksheet.write('B1', 'Nombre/Razón Social Beneficiario', bold)
        worksheet.write('C1', 'Tipo Documento', bold)
        worksheet.write('D1', 'Nº Referencia/Documento', bold)
        worksheet.write('E1', 'Monto Documento', bold)
        worksheet.write('F1', 'Subtotal', bold)
        worksheet.write('G1', 'Forma Pago', bold)
        worksheet.write('H1', 'Nº Cuenta de Abono', bold)
        worksheet.write('I1', 'Banco Destino', bold)
        worksheet.write('J1', 'Cód. Suc', bold)
        worksheet.write('K1', 'Email Aviso', bold)
        worksheet.write('L1', 'Mensaje Aviso', bold)
        # Start from the first cell below the headers.
        row = 1
        col = 0
        # Iterate over the data and write it out row by row.
        for line in self.line_ids:
            worksheet.write(row, col, line.move_id.partner_id.vat or '')
            worksheet.write(row, col + 1, line.move_id.partner_id.name or '')
            worksheet.write(row, col + 2, '*')
            worksheet.write(row, col + 3, line.move_id.name or '')
            worksheet.write(row, col + 4, '*')
            worksheet.write(row, col + 5, '*')
            worksheet.write(row, col + 6, '*')
            worksheet.write(row, col + 7, line.move_id.partner_bank_id.acc_number or '')
            worksheet.write(row, col + 8, line.move_id.partner_bank_id.bank_id.name or '')
            worksheet.write(row, col + 9, '*')
            worksheet.write(row, col + 10, line.move_id.partner_id.email or '')
            worksheet.write(row, col + 11, '*')
            row += 1
        workbook.close()
        
    def generate_payroll_xlsx(self):
        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()
        # Create a workbook and add
        workbook = xlsxwriter.Workbook(output)
        # Modifica el excel según el banco seleccionado
        if self.partner_bank_id.bank_id.format_template_xlsx:
                getattr(self, f'format_template_xlsx_{self.partner_bank_id.bank_id.format_template_xlsx}')(workbook)
        else:
            raise ValidationError(_('No existe una plantilla para el banco seleccionado.'))
        output.seek(0)
        # construct the file name
        filename = f'{self.name}-{self.partner_bank_id.acc_number}'.replace(' ', '_').replace('-', '_') + '.xlsx'
        # Get the value of the BytesIO buffer and put it in the response
        self.payroll_xlsx = base64.b64encode(output.getvalue())
        # self.payroll_xlsx = output.read().encode('base64')
        self.payroll_xlsx_filename = filename
        
        
    def convert_approved(self):
        self.state = 'approved'
    
    def print_payroll(self):
        try:
        # construir excel
            self.generate_payroll_xlsx()
        except Exception as e:
            raise ValidationError(_(e))
        else:
            download =  {
                'type': 'ir.actions.act_url',
                'url': '/web/content/payroll.payment/%s/payroll_xlsx/%s?download=true' % (self.id, self.payroll_xlsx_filename),
                'target': 'self',
            }
            self.state = 'generation_payroll'
            return download
    
    def convert_to_done(self):
        journal_id = self.env['account.journal'].search([('bank_account_id', '=', self.partner_bank_id.id)], limit=1)
        outbound_payment_method_lines = journal_id.outbound_payment_method_line_ids.filtered(lambda r: r.payment_method_id.name == 'Manual')
        account_credit = outbound_payment_method_lines and outbound_payment_method_lines[0].payment_account_id or False
        if not journal_id:
            raise ValidationError(_('No existe un diario de tipo banco.'))
        if not account_credit:
            raise ValidationError(_('No existe una cuenta de débito.'))
        self.move_id = self.env['account.move'].sudo().create({
            'state': 'draft',
            'date': self.date,
            'journal_id': journal_id.id,
            'ref': self.name,
            'name': '/',
        })
        list_line_ids = []
        for line in self.line_ids:
            account_debit = line.move_id.partner_id.property_account_payable_id
            if not account_credit:
                raise ValidationError(_('No existe una cuenta de crédito.'))
            list_line_ids.append(
                (0, 0, {
                    'account_id': account_debit.id,
                    'account_root_id': account_debit.id,
                    'name': f'Pago de nómina {line.move_id.name} debit',
                    'display_type': False,
                    'debit': line.amount_total,
                    'credit': 0,
                    'sequence': 0,
                    'amount_currency': 0,
                    'currency_id': self.currency_id.id,
                    'analytic_account_id': False,
                    'analytic_tag_ids': False,
                    'company_currency_id': self.currency_id.id,
                    'quantity': 1,
                    'product_id': False,
                })
            )
            line.move_id.payment_state = 'paid'
        list_line_ids.append(
            (0, 0, {
                'account_id': account_credit.id,
                'account_root_id': account_credit.id,
                'name': f'Pago de nómina {self.partner_bank_id.acc_number} credit',
                'display_type': False,
                'debit': 0,
                'credit': self.amount_total,
                'sequence': 0,
                'amount_currency': 0,
                'currency_id': self.currency_id.id,
                'analytic_account_id': False,
                'analytic_tag_ids': False,
                'company_currency_id': self.currency_id.id,
                'quantity': 1,
                'product_id': False,
            })
        )
        self.move_id.sudo().line_ids = list_line_ids
        # self.move_id.action_post() # todo: por confirmar si se debe postear o no el asiento contable
        self.state = 'done'
    
    def convert_to_draft(self):
        try:
            self = self.sudo()
            self.move_id.button_draft()
            self.move_id.unlink()
            self.line_ids.mapped('move_id').write(
                {'payment_state': 'not_paid'}
            )
        except Exception as e:
            raise ValidationError(_(e))
        else:
            self.state = 'draft'
        
    def action_view_line_ids(self):
        self.ensure_one()
        action = self.env.ref('payroll_payment.payroll_payment_line_action').read()[0]
        action['domain'] = [('payroll_payment_id', '=', self.id)]
        return action
