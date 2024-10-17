# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.product_configurator.tests.test_product_configurator_test_cases import (
    ProductConfiguratorTestCases,
)


class TestMrp(ProductConfiguratorTestCases):
    def setUp(self):
        super(TestMrp, self).setUp()
        self.mrpBom = self.env["mrp.bom"]
        self.mrpBomLine = self.env["mrp.bom.line"]
        self.productProduct = self.env["product.product"]
        self.mrpProduction = self.env["mrp.production"]
        self.product_id = self.env.ref("product.product_product_3")
        self.company = self.env.ref("base.main_company")

        self.selected_products = self.productProduct
        self.selected_products |= self.env.ref(
            "product_configurator.product_bmw_model_sport_line"
        )
        self.selected_products |= self.env.ref(
            "product_configurator.product_2_series_transmission_steptronic"
        )
        self.selected_products |= self.env.ref(
            "product_configurator.product_2_series_sunroof"
        )
        self.selected_products |= self.env.ref(
            "product_configurator.product_engine_220i_coupe"
        )

        self.selected_alt_products = self.productProduct
        self.selected_alt_products |= self.env.ref(
            "product_configurator.product_bmw_sport_line"
        )
        self.selected_alt_products |= self.env.ref(
            "product_configurator.product_2_series_transmission_steptronic"
        )
        self.selected_alt_products |= self.env.ref(
            "product_configurator.product_2_series_sunroof"
        )
        self.selected_alt_products |= self.env.ref(
            "product_configurator.product_engine_218i_coupe"
        )

        # create bom
        self.bom_id = self.mrpBom.create(
            {
                "product_tmpl_id": self.product_id.product_tmpl_id.id,
                "product_qty": 1.00,
                "type": "normal",
                "ready_to_produce": "all_available",
            }
        )
        # create bom line
        self.bom_line_id = self.mrpBomLine.create(
            {
                "bom_id": self.bom_id.id,
                "product_id": self.product_id.id,
                "product_qty": 1.00,
            }
        )

    def _configure_alt_variant(self):
        product_config_wizard = self.ProductConfWizard.create(
            {
                "product_tmpl_id": self.config_product.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                "__attribute_{}".format(self.attr_fuel.id): self.value_gasoline.id,
                "__attribute_{}".format(self.attr_engine.id): self.value_218i.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                "__attribute_{}".format(self.attr_color.id): self.value_red.id,
                "__attribute_{}".format(self.attr_rims.id): self.value_rims_378.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                "__attribute_{}".format(
                    self.attr_model_line.id
                ): self.value_sport_line.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                "__attribute_{}".format(self.attr_tapistry.id): self.value_tapistry.id,
            }
        )
        product_config_wizard.action_next_step()
        product_config_wizard.write(
            {
                "__attribute_{}".format(
                    self.attr_transmission.id
                ): self.value_transmission.id,
                "__attribute_{}".format(self.attr_options.id): [
                    [6, 0, [self.value_options_2.id]]
                ],
            }
        )
        return product_config_wizard.with_context(
            allowed_company_ids=[self.company.id]
        ).action_next_step()

    def _get_product_id(self):
        self._configure_product_nxt_step()
        return self.config_product.product_variant_ids[-1]

    def test_00_generate_bom_from_parent(self):
        variant = self._get_product_id()
        bom_products = variant.variant_bom_ids.bom_line_ids.mapped("product_id")

        self.assertEqual(
            bom_products,
            self.selected_products,
            "BOM was not generated correctly",
        )

    def test_01_generate_bom_from_values(self):
        self.env.ref("product_configurator_mrp.bom_2_series").active = False

        variant = self._get_product_id()
        bom_products = variant.variant_bom_ids.bom_line_ids.mapped("product_id")

        self.assertEqual(
            bom_products,
            self.selected_products,
            "BOM was not generated correctly",
        )

    def test_02_action_config_start(self):
        production = self.mrpProduction.create(
            {
                "product_id": self.product_id.id,
                "product_qty": 1.00,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": self.bom_id.id,
                "date_planned_start": datetime.now(),
            }
        )
        context = dict(
            self.env.context,
            default_order_id=production.id,
            wizard_model="product.configurator.mrp",
            allowed_company_ids=[self.company.id],
        )
        production.action_config_start()
        self.ProductConfWizard = self.env["product.configurator.mrp"].with_context(
            **context
        )
        self._configure_product_nxt_step()
        move_products = production.move_raw_ids.mapped("product_id")
        self.assertEqual(
            move_products,
            self.selected_products,
            "Production BOM not generated correctly",
        )

    def test_03_reconfigure_product(self):
        variant = self._get_product_id()
        production = self.mrpProduction.create(
            {
                "product_id": variant.id,
                "product_qty": 1.00,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "bom_id": variant.variant_bom_ids.id,
                "date_planned_start": datetime.now(),
            }
        )

        action = production.reconfigure_product()
        wiz = self.env["product.configurator.mrp"].browse(action["res_id"])
        ctx = action["context"]
        self.ProductConfWizard = wiz.with_context(**ctx)
        self._configure_alt_variant()

        move_products = production.move_raw_ids.mapped("product_id")
        self.assertEqual(
            move_products,
            self.selected_alt_products,
            "Production BOM not generated correctly",
        )

    def test_04_bom_missing_config_set(self):
        # If the user fails to (or chooses not to) specify a config set for a BOM line,
        # that BOM line will be included in all variant BOMs, even if not selected in
        # the wizard
        bom_line = self.env.ref("product_configurator_mrp.bom_line_engine_218i_coupe")
        bom_line.config_set_id = False

        variant = self._get_product_id()
        bom_products = variant.variant_bom_ids.bom_line_ids.mapped("product_id")

        selected_products = self.selected_products
        selected_products |= self.env.ref(
            "product_configurator.product_engine_218i_coupe"
        )

        self.assertEqual(
            bom_products,
            selected_products,
            "BOM was not generated correctly",
        )
