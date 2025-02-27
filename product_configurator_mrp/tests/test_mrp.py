# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from ..tests.test_product_configurator_test_cases import ProductConfiguratorTestCases


class TestMrp(ProductConfiguratorTestCases):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mrpBomConfigSet = cls.env["mrp.bom.line.configuration.set"]
        cls.mrpBomConfig = cls.env["mrp.bom.line.configuration"]
        cls.mrpBom = cls.env["mrp.bom"]
        cls.mrpBomLine = cls.env["mrp.bom.line"]
        cls.mrpRoutingWorkcenter = cls.env["mrp.routing.workcenter"]
        cls.productProduct = cls.env["product.product"]
        cls.productTemplate = cls.env["product.template"]
        cls.mrpProduction = cls.env["mrp.production"]
        cls.product_id = cls.env.ref("product.product_product_3")
        cls.workcenter_id = cls.env.ref("mrp.mrp_workcenter_3")

        # create bom
        cls.bom_id = cls.mrpBom.create(
            {
                "product_tmpl_id": cls.product_id.product_tmpl_id.id,
                "product_qty": 1.00,
                "type": "consu",
                "ready_to_produce": "all_available",
            }
        )
        # create bom line
        cls.bom_line_id = cls.mrpBomLine.create(
            {
                "bom_id": cls.bom_id.id,
                "product_id": cls.product_id.id,
                "product_qty": 1.00,
            }
        )
        # create BOM operations line
        cls.mrpRoutingWorkcenter.create(
            {
                "bom_id": cls.bom_id.id,
                "name": "Operation 1",
                "workcenter_id": cls.workcenter_id.id,
            }
        )

    def test_00_skip_bom_line(self):
        checkVal = self.mrpBomLine._skip_bom_line(product=self.product_id)
        self.assertFalse(
            checkVal,
            "Error: If value exists\
            Method: _skip_bom_line()",
        )
        self.bom_line_id.bom_id.config_ok = True
        self.mrp_config_step = self.mrpBomConfigSet.create(
            {
                "name": "TestConfigSet",
            }
        )
        self.bom_line_id.write({"config_set_id": self.mrp_config_step.id})
        # create bom_line_config
        self.mrp_bom_config = self.mrpBomConfig.create(
            {
                "config_set_id": self.mrp_config_step.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.value_gasoline.id,
                            self.value_218i.id,
                            self.value_220i.id,
                            self.value_red.id,
                        ],
                    )
                ],
            }
        )
        self.product_id.write(
            {"attribute_value_ids": [(6, 0, self.mrp_bom_config.value_ids.ids)]}
        )
        self.mrpProduction.create(
            {
                "product_id": self.product_id.id,
                "product_qty": 1.00,
                "product_uom_id": 1.00,
                "bom_id": self.bom_id.id,
                "date_planned_start": datetime.now(),
            }
        )
        self.mrpBomLine._skip_bom_line(product=self.product_id)
        self.assertFalse(
            checkVal,
            "Error: If value exists\
            Method: _skip_bom_line()",
        )

    def test_01_action_config_start(self):
        mrpProduction = self.mrpProduction.create(
            {
                "product_id": self.product_id.id,
                "product_qty": 1.00,
                "product_uom_id": 1.00,
                "bom_id": self.bom_id.id,
                "date_planned_start": datetime.now(),
            }
        )
        context = dict(
            self.env.context,
            default_order_id=mrpProduction.id,
            wizard_model="product.configurator.mrp",
        )
        mrpProduction.action_config_start()
        self.ProductConfWizard = self.env["product.configurator.mrp"].with_context(
            **context
        )
        self._configure_product_nxt_step()
        # self.assertEqual(
        #     vals['res_id'],
        #     mrpProduction.product_id.id,
        #     'Not Equal'
        # )
