#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import operator
from functools import reduce

from odoo.tests import HttpCase, tagged

from .test_website_product_configurator_values import TestProductConfiguratorValues


@tagged("post_install", "-at_install")
class TestReconfigureProductHTTP(HttpCase, TestProductConfiguratorValues):
    def test_tour(self):
        admin_user = self.env.ref("base.user_admin")

        session = self.session_id
        session.user_id = admin_user
        pavs_xmlids = [
            "product_configurator.product_attribute_value_gasoline",
            "product_configurator.product_attribute_value_218i",
            "product_configurator.product_attribute_value_steptronic",
            "product_configurator.product_attribute_value_silver",
            "product_configurator.product_attribute_value_rims_378",
            "product_configurator.product_attribute_value_tapistry_black",
            "product_configurator.product_attribute_value_sport_line",
            "product_configurator.product_attribute_value_armrest",
        ]
        pavs_list = [self.env.ref(xmlid) for xmlid in pavs_xmlids]
        session.value_ids = reduce(operator.or_, pavs_list)
        session.action_confirm()

        session_url = "/product_configurator/product/%s" % session.id
        self.start_tour(
            session_url,
            "website_product_configurator.reconfigure_cart_line",
            login=admin_user.login,
        )
