from odoo import api, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.model
    def get_attribute_value_extra_prices(
        self, product_tmpl_id, pt_attr_value_ids, pricelist=None
    ):
        # Sudo to bypass access right for Public User
        return super(
            ProductAttributeValue, self.sudo()
        ).get_attribute_value_extra_prices(
            product_tmpl_id, pt_attr_value_ids, pricelist
        )
