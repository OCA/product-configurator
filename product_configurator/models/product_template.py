from odoo import api, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        domain = args or []
        domain += ["|", ("name", operator, name), ("default_code", operator, name)]
        return self.search(domain, limit=limit).name_get()
        