# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ProductConfiguratorPurchase(models.TransientModel):

    _name = "product.configurator.purchase"
    _inherit = "product.configurator"
    _description = "Product Configurator Purchase"

    order_id = fields.Many2one(
        comodel_name="purchase.order", required=True, readonly=True
    )
    order_line_id = fields.Many2one(comodel_name="purchase.order.line", readonly=True)

    def _get_order_line_vals(self, product_id):
        """Hook to allow custom line values to be put on the newly
        created or edited lines."""
        product = self.env["product.product"].browse(product_id)
        return {
            "product_id": product_id,
            "product_qty": 1,
            "name": product._get_mako_tmpl_name(),
            "product_uom": product.uom_id.id,
            "date_planned": fields.Datetime.now(),
            "config_session_id": self.config_session_id.id,
            "price_unit": self.config_session_id.price,
        }

    def action_config_done(self):
        """Parse values and execute final code before closing the wizard"""
        res = super(ProductConfiguratorPurchase, self).action_config_done()
        if res.get("res_model") == self._name:
            return res
        model_name = "purchase.order.line"
        line_vals = self._get_order_line_vals(res["res_id"])
        order_line_obj = self.env[model_name]
        cfg_session = self.config_session_id
        specs = cfg_session.get_onchange_specifications(model=model_name)
        updates = order_line_obj.onchange(line_vals, ["product_id"], specs)
        values = updates.get("value", {})
        values = cfg_session.get_vals_to_write(values=values, model=model_name)
        values.update(line_vals)
        if values.get("taxes_id"):
            taxes_id = []
            for line in values.get("taxes_id")[1:]:
                taxes_id.append(line[1])
            values["taxes_id"] = [(6, 0, taxes_id)]
        if self.order_line_id:
            self.order_line_id.write(values)
        else:
            values.update({"order_id": self.order_id.id})
            self.order_id.order_line.create(values)
        return

    @api.model
    def create(self, vals):
        if self.env.context.get("default_order_line_id", False):
            sale_line = self.env["purchase.order.line"].browse(
                self.env.context["default_order_line_id"]
            )
            if sale_line.custom_value_ids:
                vals["custom_value_ids"] = self._get_custom_values(
                    sale_line.config_session_id
                )
        res = super(ProductConfiguratorPurchase, self).create(vals)
        return res

    def _get_custom_values(self, session):
        custom_values = [(5,)] + [
            (
                0,
                0,
                {
                    "attribute_id": value_custom.attribute_id.id,
                    "value": value_custom.value,
                    "attachment_ids": [
                        (4, attach.id) for attach in value_custom.attachment_ids
                    ],
                },
            )
            for value_custom in session.custom_value_ids
        ]
        return custom_values
