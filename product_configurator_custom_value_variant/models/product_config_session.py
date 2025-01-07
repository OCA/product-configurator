# Copyright 2025 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductConfigSession(models.Model):
    _inherit = "product.config.session"

    def _create_custom_attribute_values(self, value_ids=None, custom_vals=None):
        """Create new attribute values and assign them to `self`."""
        if value_ids is None:
            value_ids = self.value_ids.ids

        if custom_vals is None:
            custom_vals = self._get_custom_vals_dict()

        new_attribute_values = self.env["product.attribute.value"].browse()
        session_custom_values_to_unlink = self.env[
            "product.config.session.custom.value"
        ].browse()
        for attribute_id, custom_value in custom_vals.copy().items():
            attribute = self.env["product.attribute"].browse(attribute_id)
            if attribute.create_attribute_value:
                custom_attribute_value = attribute._get_variant_custom_attribute_value(
                    str(custom_value)
                )

                value_ids.append(custom_attribute_value.id)
                new_attribute_values |= custom_attribute_value

                custom_vals.pop(attribute_id, None)
                session_custom_value_to_unlink = self.custom_value_ids.filtered(
                    lambda session_custom_value: session_custom_value.attribute_id
                    == attribute
                )
                if session_custom_value_to_unlink:
                    session_custom_values_to_unlink |= session_custom_value_to_unlink

        if new_attribute_values:
            self.value_ids |= new_attribute_values
            self.value_ids -= self.get_custom_value_id()
            for attribute in new_attribute_values.attribute_id:
                attribute_line = self.product_tmpl_id.attribute_line_ids.filtered(
                    lambda ptav: ptav.attribute_id == attribute
                )
                attribute_line.value_ids |= new_attribute_values.filtered(
                    lambda pav: pav.attribute_id == attribute
                )

        if session_custom_values_to_unlink:
            session_custom_values_to_unlink.unlink()

        return new_attribute_values

    def create_get_variant(
        self,
        value_ids=None,
        custom_vals=None,
    ):
        new_attribute_values = self._create_custom_attribute_values(
            value_ids=value_ids,
            custom_vals=custom_vals,
        )
        variant = super().create_get_variant(
            value_ids=value_ids,
            custom_vals=custom_vals,
        )

        if new_attribute_values:
            # The new attribute values must not be available for new models
            for attribute_line in self.product_tmpl_id.attribute_line_ids:
                attribute_line.with_context(
                    no_remove_custom_variants=variant.ids,
                ).value_ids -= (
                    attribute_line.value_ids & new_attribute_values
                )
        return variant
