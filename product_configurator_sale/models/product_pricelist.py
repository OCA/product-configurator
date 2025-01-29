from odoo import models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    def _compute_base_price(self, product, quantity, uom, date, target_currency):
        if self.env.context.get("config_price"):
            price = self.env.context.get("config_price")
        else:
            price = super()._compute_base_price(
                product, quantity, uom, date, target_currency
            )
        return price
