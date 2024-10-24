#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductConfigSession(models.Model):
    _inherit = "product.config.session"

    @api.model
    def get_cfg_price(self, value_ids=None, custom_vals=None):
        price = super().get_cfg_price(value_ids=value_ids, custom_vals=custom_vals)

        if value_ids is None:
            value_ids = self.value_ids.ids

        product = self.product_id
        product_template = self.product_tmpl_id
        ptavs = self.env["product.template.attribute.value"].search(
            [
                ("product_attribute_value_id", "in", value_ids),
                ("product_tmpl_id", "=", product_template.id),
            ]
        )
        for ptav in ptavs:
            formula_extra_price = ptav._eval_extra_price_formula(
                product,
                config_session=self,
            )
            price += formula_extra_price

        return price
