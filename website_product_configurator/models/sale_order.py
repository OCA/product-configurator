import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_order_line_values(
        self,
        product_id,
        quantity,
        linked_line_id=False,
        no_variant_attribute_values=None,
        product_custom_attribute_values=None,
        **kwargs
    ):
        values = super()._prepare_order_line_values(
            product_id,
            quantity,
            linked_line_id=linked_line_id,
            no_variant_attribute_values=no_variant_attribute_values,
            product_custom_attribute_values=product_custom_attribute_values,
            **kwargs,
        )
        config_session_id_str = kwargs.get("config_session_id")
        if config_session_id_str is not None:
            values["config_session_id"] = int(config_session_id_str)
            if "product_config_session" in request.session:
                # The current configuration has been assigned to an order line,
                # new configurations will go in new order lines
                del request.session["product_config_session"]
        return values

    def _prepare_order_line_update_values(self, order_line, quantity, **kwargs):
        update_values = super()._prepare_order_line_update_values(
            order_line, quantity, **kwargs
        )
        reconfiguring_product_id = kwargs.get("reconfiguring_product_id")
        config_session_id = kwargs.get("config_session_id")
        if reconfiguring_product_id and config_session_id:
            reconfiguring_product = self.env["product.product"].browse(
                int(reconfiguring_product_id)
            )
            config_session = self.env["product.config.session"].browse(
                int(config_session_id)
            )
            if reconfiguring_product.exists() and config_session.exists():
                update_values["config_session_id"] = config_session.id
                update_values["product_id"] = reconfiguring_product.id
        return update_values

    def _cart_find_product_line(self, product_id, line_id=None, **kwargs):
        """Include Config session in search."""
        order_line = super()._cart_find_product_line(
            product_id, line_id=line_id, **kwargs
        )
        # Onchange quantity in cart
        if line_id:
            return order_line

        config_session_id = kwargs.get("config_session_id", False)
        if not config_session_id:
            return order_line

        order_line = order_line.filtered(
            lambda p: p.config_session_id.id == int(config_session_id)
        )
        return order_line
