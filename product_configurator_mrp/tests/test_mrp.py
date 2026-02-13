# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo.tests import RecordCapturer

from odoo.addons.product_configurator.tests.common import ProductConfiguratorTestCases


class TestMrp(ProductConfiguratorTestCases):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_configurator_model()

    @classmethod
    def setup_configurator_model(cls):
        """
        Set the configurator model on the test class so that future calls to
        _configure_product_nxt_step will do manufacturing configuration instead
        of product configuration.
        """
        action = (
            cls.env["mrp.production"]
            .with_context(allowed_company_ids=cls.env.companies.ids)
            .action_config_start()
        )

        cls.ProductConfWizard = cls.env[action["res_model"]].with_context(
            **action.get("context", {})
        )

    def get_record_from_action(self, action: dict) -> "odoo.model.base":
        target = self.env[action["res_model"]].browse(action.get("res_id")).exists()
        action_context = action.get("context", {})
        return target.with_context(**action_context)

    def create_record_from_action(
        self, action: dict, create_vals: "odoo.values.base"
    ) -> "odoo.model.base":
        target = self.get_record_from_action(action)
        assert not target, "Action opens existing record!"
        return target.create(create_vals)

    def run_mrp_configuration_flow(
        self,
    ) -> tuple[
        "odoo.model.mrp_production", "odoo.model.mrp_bom", "odoo.model.product_product"
    ]:
        """
        Run a pre-set manufacturing configuration flow.

        Return the generated MO, any generated BoMs and any generated variants.
        """
        with (
            RecordCapturer(self.env["product.product"], []) as prod_capturer,
            RecordCapturer(self.env["mrp.bom"], []) as bom_capturer,
        ):
            last_action = self._configure_product_nxt_step()
        mo = self.get_record_from_action(last_action)
        return mo, bom_capturer.records, prod_capturer.records

    def test_configure_new_product(self):
        mo, new_bom, new_product = self.run_mrp_configuration_flow()

        self.assertTrue(
            new_product,
            msg="The configurator should have generated a new product as no match "
            "existed before",
        )
        self.assertTrue(
            new_bom,
            msg="The configurator should have generated a new bom as no match existed "
            "before",
        )
        self.assertEqual(
            mo._name,
            "mrp.production",
            msg="The last step should open a manufacturing order for the configured "
            "product",
        )
        self.assertEqual(mo.product_id, new_product)
        self.assertEqual(mo.bom_id, new_bom)

        mo_2, no_bom, no_product = self.run_mrp_configuration_flow()

        self.assertFalse(
            no_bom,
            "A second run with the same configuration should re-use the previously "
            "generated bom",
        )
        self.assertEqual(
            mo_2.bom_id,
            new_bom,
            "A second run with the same configuration should re-use the previously "
            "generated bom",
        )
        self.assertFalse(
            no_product,
            "A second run with the same configuration should re-use the previously "
            "generated product",
        )
        self.assertEqual(
            mo_2.product_id,
            new_product,
            "A second run with the same configuration should re-use the previously "
            "generated product",
        )
