from odoo.http import request, route

from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class ProductConfiguratorController(WebsiteSaleProductConfiguratorController):
    @route()
    def website_sale_should_show_product_configurator(
        self, product_template_id, ptav_ids, is_product_configured
    ):
        product_template = request.env["product.template"].browse(product_template_id)
        if product_template.config_ok:
            return False
        return super().website_sale_should_show_product_configurator(
            product_template_id, ptav_ids, is_product_configured
        )
