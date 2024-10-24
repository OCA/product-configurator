#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCustomValues(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        length_att = cls.env["product.attribute"].create(
            {
                "name": "Length",
                "value_ids": [
                    Command.create(
                        {
                            "name": "5",
                        }
                    ),
                    Command.create(
                        {
                            "name": "10",
                        }
                    ),
                ],
                "val_custom": True,
                "custom_type": "integer",
            }
        )

        # Create Template Product
        cls.template = cls.env["product.template"].create(
            {
                "name": "Glass",
                "config_ok": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": length_att.id,
                            "custom": True,
                            "value_ids": [
                                Command.set(length_att.value_ids.ids),
                            ],
                        }
                    ),
                ],
            }
        )

    def test_configuration(self):
        """The selected custom value is propagated to the sale order line."""
        self.start_tour(
            "/shop",
            "website_product_configurator.custom_values",
            login="admin",
        )
