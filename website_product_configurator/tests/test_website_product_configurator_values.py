from datetime import timedelta

from odoo import fields

from odoo.addons.product_configurator.tests import test_product_configurator_test_cases


class TestProductConfiguratorValues(
    test_product_configurator_test_cases.ProductConfiguratorTestCases
):
    def setUp(self):
        super(TestProductConfiguratorValues, self).setUp()
        self.productConfigStepLine = self.env["product.config.step.line"]
        self.productAttributeLine = self.env["product.template.attribute.line"]
        self.product_category = self.env.ref("product.product_category_5")
        self.value_diesel = self.env.ref(
            "product_configurator.product_attribute_value_diesel"
        )
        self.value_218d = self.env.ref(
            "product_configurator.product_attribute_value_218d"
        )
        self.value_220d = self.env.ref(
            "product_configurator.product_attribute_value_220d"
        )
        self.config_step_engine = self.env.ref(
            "product_configurator.config_step_engine"
        )
        self.product_tmpl_id = self.env["product.template"].create(
            {
                "name": "Test Configuration",
                "config_ok": True,
                "type": "consu",
                "categ_id": self.product_category.id,
            }
        )
        self.attributeLine1 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attr_fuel.id,
                "value_ids": [(6, 0, [self.value_gasoline.id, self.value_diesel.id])],
                "required": True,
            }
        )
        self.attributeLine2 = self.productAttributeLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "attribute_id": self.attr_engine.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.value_218i.id,
                            self.value_220i.id,
                            self.value_218d.id,
                            self.value_220d.id,
                        ],
                    )
                ],
                "required": True,
            }
        )
        self.configStepLine = self.productConfigStepLine.create(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "config_step_id": self.config_step_engine.id,
                "attribute_line_ids": [
                    (6, 0, [self.attributeLine1.id, self.attributeLine2.id])
                ],
            }
        )
        self.config_product = self.env.ref("product_configurator.bmw_2_series")
        self.config_product_1 = self.env.ref(
            "product_configurator.product_config_line_gasoline_engines"
        )
        self.productConfigSession = self.env["product.config.session"]
        self.session_id = self.productConfigSession.create(
            {
                "product_tmpl_id": self.config_product.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.value_gasoline.id,
                            self.value_transmission.id,
                            self.value_red.id,
                        ],
                    )
                ],
                "user_id": self.env.user.id,
                "write_date": fields.Datetime.now() - timedelta(days=5),
            }
        )
        self.session_id2 = self.productConfigSession.create(
            {
                "product_tmpl_id": self.config_product_1.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.value_gasoline.id,
                            self.value_transmission.id,
                            self.value_red.id,
                        ],
                    )
                ],
                "user_id": self.env.user.id,
                "write_date": fields.Datetime.now(),
            }
        )
