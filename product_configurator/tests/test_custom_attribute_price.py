#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import first
from odoo.tests import Form, TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestCustomAttributePrice(TransactionCase):
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

        custom_attribute_form = Form(configuration_attribute_model)
        custom_attribute_form.name = "Test custom attribute"
        custom_attribute_form.val_custom = True
        cls.custom_attribute = custom_attribute_form.save()
        cls.custom_attribute_value = cls.env.ref(
            "product_configurator.custom_attribute_value"
        )

        regular_attribute_form = Form(configuration_attribute_model)
        regular_attribute_form.name = "Test custom attribute"
        regular_attribute_form.val_custom = False
        with regular_attribute_form.value_ids.new() as value:
            value.name = "Test value 1"
        cls.regular_attribute = regular_attribute_form.save()

        product_template_form = Form(cls.env["product.template"])
        product_template_form.name = "Test configurable product"
        with product_template_form.attribute_line_ids.new() as custom_line:
            custom_line.attribute_id = cls.custom_attribute
        with product_template_form.attribute_line_ids.new() as regular_line:
            regular_line.attribute_id = cls.regular_attribute
            regular_line.value_ids.add(first(cls.regular_attribute.value_ids))
        product_template = product_template_form.save()
        product_template.config_ok = True
        cls.product_template = product_template

    def test_integer_multiplier_formula(self):
        """The custom attribute has a formula `custom_value` * `multiplier`,
        check that the configuration's price is computed correctly.
        """
        # Arrange
        regular_attribute = self.regular_attribute

        multiplier = 5
        custom_value = 3
        custom_attribute = self.custom_attribute
        custom_attribute.custom_type = "integer"
        custom_attribute.configurator_extra_price_formula = (
            "price = custom_value * %s" % multiplier
        )
        custom_attribute_value = self.custom_attribute_value

        product_template = self.product_template

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
                field_prefix
                + str(regular_attribute.id): first(regular_attribute.value_ids).id,
                field_prefix + str(custom_attribute.id): custom_attribute_value.id,
                custom_field_prefix + str(custom_attribute.id): custom_value,
            }
        )
        wizard.action_config_done()

        # Assert
        configured_session = wizard.config_session_id
        configured_custom_value = configured_session.custom_value_ids
        self.assertEqual(configured_custom_value.price, custom_value * multiplier)

        expected_configuration_price = (
            product_template.list_price + configured_custom_value.price
        )
        self.assertEqual(configured_session.price, expected_configuration_price)

        # Act: change the custom value
        new_custom_value = 2
        configured_custom_value.value = "%s" % new_custom_value

        # Assert: the price has changed
        new_expected_custom_price = new_custom_value * multiplier
        self.assertEqual(configured_custom_value.price, new_expected_custom_price)

        new_expected_configuration_price = (
            product_template.list_price + configured_custom_value.price
        )
        self.assertEqual(configured_session.price, new_expected_configuration_price)
