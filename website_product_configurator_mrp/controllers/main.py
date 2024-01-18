# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteProductConfigMrp(WebsiteSale):
    @http.route()
    def cart_update_json(self, product_id, **kw):
        product = request.env["product.product"].browse(int(product_id))
        if product.config_ok and kw.get("assembly") == "kit":
            attr_value_ids = product.product_template_attribute_value_ids
            attr_products = attr_value_ids.mapped(
                "product_attribute_value_id.product_id"
            )
            if not attr_products:
                return super().cart_update_json(product_id, **kw)

            for attr_product in attr_products:
                res = super().cart_update_json(attr_product.id, **kw)
            return res
        else:
            return super().cart_update_json(product_id, **kw)
