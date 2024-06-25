from openerp import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    customer_remarks = fields.Text(
        string='Customer Remarks',
        readonly=True
    )
