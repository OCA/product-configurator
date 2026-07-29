from odoo import models


class ProductConfigSession(models.Model):
    _inherit = "product.config.session"

    def create_get_variant(self, value_ids=None, custom_vals=None):
        return super(ProductConfigSession, self.sudo()).create_get_variant(
            value_ids=value_ids, custom_vals=custom_vals
        )
