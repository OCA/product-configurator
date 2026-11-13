from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _website_show_quick_add(self):
        """Override to hide quick add button (the cart button on product card at tree
        view) if the template is configured."""
        self.ensure_one()
        if self.product_tmpl_id.config_ok:
            return False
        return super()._website_show_quick_add()
