# Copyright 2025 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.tests.common import BaseCommon


class TestConfigure(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The product attribute view only shows configuration fields
        # (such as `val_custom`)
        # when called with a specific context
        # that is set by this action
        configuration_attributes_action = cls.env.ref(
            "product_configurator.action_attributes_view"
        )
        action_eval_context = configuration_attributes_action._get_eval_context()
        configuration_attribute_context = safe_eval(
            configuration_attributes_action.context, globals_dict=action_eval_context
        )
        configuration_attribute_model = cls.env["product.attribute"].with_context(
            **configuration_attribute_context
        )

        length_attribute_form = Form(configuration_attribute_model)
        length_attribute_form.name = "Length"
        with length_attribute_form.value_ids.new() as value:
            value.name = "5"
        with length_attribute_form.value_ids.new() as value:
            value.name = "10"
        length_attribute_form.val_custom = True
        length_attribute_form.create_attribute_value = True
        cls.length_attribute = length_attribute_form.save()
        cls.custom_attribute_value = cls.env.ref(
            "product_configurator.custom_attribute_value"
        )

        glass_product_template_form = Form(cls.env["product.template"])
        glass_product_template_form.name = "Glass"
        with glass_product_template_form.attribute_line_ids.new() as length_attribute_line:
            length_attribute_line.attribute_id = cls.length_attribute
            for value in cls.length_attribute.value_ids:
                length_attribute_line.value_ids.add(value)
        glass_product_template_form.config_ok = True
        cls.glass_product_template = glass_product_template_form.save()

    def test_custom_value_creates_value(self):
        """If the custom attribute is "Create attribute value",
        when used a new variant will be created, linked to a new attribute value.
        """
        # Arrange
        product_template = self.glass_product_template
        product_variants = product_template.product_variant_ids
        custom_attribute = self.length_attribute
        custom_attribute_value = self.custom_attribute_value
        custom_value = "15"
        # pre-condition
        self.assertTrue(custom_attribute.create_attribute_value)

        # Act: configure the product
        wizard_action = product_template.configure_product()
        wizard = self.env[wizard_action["res_model"]].browse(wizard_action["res_id"])
        self.assertEqual(wizard.state, "select")
        wizard.action_next_step()
        self.assertEqual(wizard.state, "configure")
        fields_prefixes = wizard._prefixes
        field_prefix = fields_prefixes.get("field_prefix")
        custom_field_prefix = fields_prefixes.get("custom_field_prefix")
        wizard.write(
            {
                field_prefix + str(custom_attribute.id): custom_attribute_value.id,
                custom_field_prefix + str(custom_attribute.id): custom_value,
            }
        )
        wizard.action_config_done()

        # Assert
        configured_session = wizard.config_session_id
        configured_variant = configured_session.product_id
        self.assertNotIn(configured_variant, product_variants)
        self.assertIn(configured_variant, product_template.product_variant_ids)

        new_attribute_value = configured_session.value_ids
        self.assertFalse(configured_session.custom_value_ids)
        self.assertIn(new_attribute_value, configured_session.value_ids)
        self.assertNotIn(
            new_attribute_value, configured_variant.attribute_line_ids.value_ids
        )
