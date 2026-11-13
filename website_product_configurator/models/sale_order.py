from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update_order_line(self, order_line, quantity, **kwargs):
        """Inherit: To update the context of sale order line."""
        self.ensure_one()
        product_variant = order_line.product_id
        # Retrieve the config session ID from multiple sources:
        config_session_id = (
            kwargs.get("config_session_id", False)
            or self.env.context.get("default_config_session_id", False)
            or (
                order_line.config_session_id.id
                if order_line.config_session_id
                else False
            )
        )
        # If still not found and it's a configurable product, try to get
        # from existing line
        if not config_session_id and order_line and product_variant.config_ok:
            # If the config session ID is not provided and line ID is given,
            # find the corresponding order line and retrieve the config
            # session ID.
            order_line = self._cart_find_product_line(
                product_variant.id,
                order_line.product_uom_id.id,
                order_line.id,
                **kwargs,
            )[:1]
            config_session_id = order_line.config_session_id.id

        ctx = {}
        # Convert config session ID to integer if it exists.
        if config_session_id and product_variant.config_ok:
            config_session_id = int(config_session_id)
            # Set the context with config session ID and current sale line.
            ctx = {
                "current_sale_line": order_line.id,
                "default_config_session_id": config_session_id,
            }
            # Also ensure config_session_id is in kwargs for downstream calls
            kwargs["config_session_id"] = config_session_id

        return super(SaleOrder, self.with_context(**ctx))._cart_update_order_line(
            order_line, quantity, **kwargs
        )

    def _cart_update_line_quantity(self, line_id, quantity, **kwargs):
        """
        Ensure config_session_id is passed through from existing line if not in kwargs.
        """
        # If config_session_id is not in kwargs, try to get it from the existing line
        if "config_session_id" not in kwargs or not kwargs.get("config_session_id"):
            order_line = self.order_line.filtered(lambda sol: sol.id == line_id)
            if order_line and order_line.config_session_id:
                kwargs["config_session_id"] = order_line.config_session_id.id

        return super()._cart_update_line_quantity(line_id, quantity, **kwargs)

    def _cart_find_product_line(self, *args, **kwargs):
        """Include Config session in search."""
        order_line = super()._cart_find_product_line(*args, **kwargs)
        # Check if config_session_id is provided.
        config_session_id = kwargs.get("config_session_id", False)

        # If a line ID is provided, return the initial product line.
        if not config_session_id or not config_session_id.isdigit():
            # Return the original order line if config_session_id is undefinded.
            return order_line

        # Filter the product line based on the config_session_id.
        order_line = order_line.filtered(
            lambda p: p.config_session_id.id == int(config_session_id)
        )
        return order_line

    def _prepare_order_line_values(
        self,
        product_id,
        quantity,
        uom_id,
        linked_line_id=False,
        no_variant_attribute_values=None,
        product_custom_attribute_values=None,
        **kwargs,
    ):
        """Inherit: Skip the creating product_variant based on received_combination for
        the configurable products."""
        self.ensure_one()
        product = self.env["product.product"].browse(product_id)
        if not product.product_tmpl_id.config_ok:
            return super()._prepare_order_line_values(
                product_id=product_id,
                quantity=quantity,
                uom_id=uom_id,
                linked_line_id=linked_line_id,
                no_variant_attribute_values=no_variant_attribute_values,
                product_custom_attribute_values=product_custom_attribute_values,
                kwargs=kwargs,
            )
        values = {
            "product_id": product.id,
            "product_uom_qty": quantity,
            "order_id": self.id,
            "linked_line_id": linked_line_id,
        }
        # Add config_session_id if provided in kwargs
        if config_session_id := kwargs.get("config_session_id", False):
            values["config_session_id"] = int(config_session_id)
        return values
