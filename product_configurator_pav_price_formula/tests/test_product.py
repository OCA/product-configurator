#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.product_attribute_value_price_formula.tests.common import TestCommon


class TestCustomAttributePrice(TestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        configurable_product_template_form = Form(cls.env["product.template"])
        configurable_product_template_form.name = "Test configurable product"
        configurable_product_template_form.list_price = 0
        with configurable_product_template_form.attribute_line_ids.new() as line:
            line.attribute_id = cls.attribute
            line.value_ids.add(cls.attribute_value)
            line.value_ids.add(cls.formula_attribute_value)
        configurable_product_template = configurable_product_template_form.save()
        configurable_product_template.config_ok = True
        cls.configurable_product_template = configurable_product_template

    def test_configure_formula_attribute(self):
        """The attribute of a configurable product has a formula,
        check that it is evaluated during the configuration.
        """
        # Arrange
        formula_price = self.formula_price
        product_template = self.product_template
        formula_attribute_value = self.formula_attribute_value
        formula_attribute = formula_attribute_value.attribute_id

        # Act: configure the product
        wizard_action = product_template.configure_product()
        wizard = self.env[wizard_action["res_model"]].browse(wizard_action["res_id"])
        self.assertEqual(wizard.state, "select")
        wizard.action_next_step()
        self.assertEqual(wizard.state, "configure")
        fields_prefixes = wizard._prefixes
        field_prefix = fields_prefixes.get("field_prefix")
        wizard.write(
            {
                field_prefix + str(formula_attribute.id): formula_attribute_value.id,
            }
        )
        wizard.action_config_done()

        # Assert
        configured_session = wizard.config_session_id
        expected_configuration_price = product_template.list_price + formula_price
        self.assertEqual(configured_session.price, expected_configuration_price)
