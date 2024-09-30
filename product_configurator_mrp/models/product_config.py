# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductConfigSession(models.Model):
    _inherit = "product.config.session"

    def create_get_bom(self, variant, product_tmpl_id=None, values=None):
        if values is None:
            values = {}
        if product_tmpl_id is None or variant.product_tmpl_id != product_tmpl_id:
            product_tmpl_id = variant.product_tmpl_id

        mrpBom = self.env["mrp.bom"]
        mrpBomLine = self.env["mrp.bom.line"]
        attr_products = variant.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id.product_id"
        )
        attr_values = variant.product_template_attribute_value_ids.mapped(
            "product_attribute_value_id"
        )
        existing_bom = self.env["mrp.bom"].search(
            [
                ("product_tmpl_id", "=", product_tmpl_id.id),
                ("product_id", "=", variant.id),
            ]
        )
        if existing_bom:
            return existing_bom[:1]

        parent_bom = self.env["mrp.bom"].search(
            [
                ("product_tmpl_id", "=", product_tmpl_id.id),
                ("product_id", "=", False),
            ],
            order="sequence asc",
            limit=1,
        )
        bom_lines = []
        if not parent_bom:
            # If not Bom, then Cycle through attributes to add their
            # related products to the bom lines.
            for product in attr_products:
                bom_line_vals = {"product_id": product.id}
                specs = self.get_onchange_specifications(model="mrp.bom.line")
                updates = mrpBomLine.onchange(bom_line_vals, ["product_id"], specs)
                values = updates.get("value", {})
                values = self.get_vals_to_write(values=values, model="mrp.bom.line")
                values.update(bom_line_vals)
                bom_lines.append((0, 0, values))
        else:
            # If parent BOM is used, then look through Config Sets
            # on parent product's bom to add the products to the bom lines.
            for parent_bom_line in parent_bom.bom_line_ids:
                if parent_bom_line.config_set_id:
                    for config in parent_bom_line.config_set_id.configuration_ids:
                        # Add bom lines if config values are part of attr_values
                        if set(config.value_ids.ids).issubset(set(attr_values.ids)):
                            for (
                                config_bom_line
                            ) in parent_bom_line.config_set_id.bom_line_ids:
                                if config_bom_line.bom_id.id == parent_bom.id:
                                    parent_bom_line_vals = {
                                        "product_id": config_bom_line.product_id.id
                                    }
                                    specs = self.get_onchange_specifications(
                                        model="mrp.bom.line"
                                    )
                                    updates = mrpBomLine.onchange(
                                        parent_bom_line_vals, ["product_id"], specs
                                    )
                                    values = updates.get("value", {})
                                    values = self.get_vals_to_write(
                                        values=values, model="mrp.bom.line"
                                    )
                                    values.update(parent_bom_line_vals)
                                    bom_lines.append((0, 0, values))
                else:
                    parent_bom_line_vals = {"product_id": parent_bom_line.product_id.id}
                    specs = self.get_onchange_specifications(model="mrp.bom.line")
                    updates = mrpBomLine.onchange(
                        parent_bom_line_vals, ["product_id"], specs
                    )
                    values2 = updates.get("value", {})
                    values2 = self.get_vals_to_write(
                        values=values, model="mrp.bom.line"
                    )
                    values2.update(parent_bom_line_vals)
                    bom_lines.append((0, 0, values2))
        if bom_lines:
            bom_values = {
                "product_tmpl_id": self.product_tmpl_id.id,
                "product_id": variant.id,
                "bom_line_ids": bom_lines,
            }
            specs = self.get_onchange_specifications(model="mrp.bom")
            updates = mrpBom.onchange(
                bom_values,
                ["product_id", "product_tmpl_id", "bom_line_ids"],
                specs,
            )
            values = updates.get("value", {})
            values = self.get_vals_to_write(values=values, model="mrp.bom")
            values.update(bom_values)
            mrp_bom_id = mrpBom.create(values)
            return mrp_bom_id
        return False

    def create_get_variant(self, value_ids=None, custom_vals=None):
        variant = super(ProductConfigSession, self).create_get_variant(
            value_ids=value_ids, custom_vals=custom_vals
        )
        self.create_get_bom(variant=variant, product_tmpl_id=self.product_tmpl_id)
        return variant
