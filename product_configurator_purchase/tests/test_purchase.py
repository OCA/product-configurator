from datetime import datetime

from odoo.addons.product_configurator.tests import (
    common as TC,
)


class PurchaseOrder(TC.ProductConfiguratorTestCases):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PurchaseOrder = cls.env["purchase.order"]
        cls.productPricelist = cls.env["product.pricelist"]
        cls.resPartner = cls.env.ref("product_configurator_purchase.partenr_purchase_1")
        cls.currency_id = cls.env.ref("base.USD")
        cls.company_id = cls.env.ref("base.main_company")
        cls.ProductConfWizard = cls.env["product.configurator.purchase"]

        cls.config_product = cls.env.ref("product_configurator.bmw_2_series")

    def test_00_reconfigure_product(self):
        product_id = self.env["product.product"].create(
            {"product_tmpl_id": self.config_product.id, "name": "Test Product"}
        )
        purchase_order_id = self.PurchaseOrder.create(
            {
                "partner_id": self.resPartner.id,
                "currency_id": self.currency_id.id,
                "date_order": datetime.now(),
                "date_planned": datetime.now(),
                "company_id": self.company_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product_id.id,
                        },
                    )
                ],
            }
        )
        context = dict(
            default_order_id=purchase_order_id.id,
            wizard_model="product.configurator.purchase",
        )

        self.ProductConfWizard = self.env["product.configurator.purchase"].with_context(
            **context
        )
        purchase_order_id.action_config_start()
        product_tmpl_id = purchase_order_id.order_line.product_id.product_tmpl_id.id
        self.ProductConfWizard.create(
            {"order_id": purchase_order_id.id, "product_tmpl_id": product_tmpl_id}
        )
        purchase_order_id.order_line.reconfigure_product()
        product_tmpl = purchase_order_id.order_line.product_id.product_tmpl_id
        self.assertEqual(
            product_tmpl.id,
            self.config_product.id,
            "Error: If product_tmpl not exsits\
            Method: action_config_start()",
        )
