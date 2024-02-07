#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import operator
from functools import reduce

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

# Found no way to wrap this nicely enough for linters
from odoo.addons.website_product_configurator.tests.test_website_product_configurator_values import (  # noqa: B950
    TestProductConfiguratorValues,
)

MODULE_NAME = "website_product_configurator_hide_price"
TEST_BROWSER_PATH = (
    "odoo.addons.%s.tests.test_hide_price.TestHidePrice.browser" % MODULE_NAME
)


@tagged("post_install", "-at_install")
class TestHidePrice(HttpCase, TestProductConfiguratorValues):
    def test_tour_hide_price(self):
        """If a configured product has `website_hide_price` enabled,
        the price is hidden and the message is shown.
        """
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
        product = session.product_id
        product.website_hide_price = True
        product.website_hide_price_message = "Price is hidden"

        session_url = "/product_configurator/product/%s" % session.id
        self.start_tour(
            session_url,
            "website_product_configurator_hide_price.show_message",
            login=admin_user.login,
        )
        # There is no way to assert that a node is missing in tours,
        # so we check that the tour fails.
        with self.assertRaises(AssertionError) as ae, mute_logger(TEST_BROWSER_PATH):
            self.start_tour(
                session_url,
                "website_product_configurator_hide_price.show_price",
                login=admin_user.login,
            )
        exc_message = ae.exception.args[0]
        self.assertIn("failed at step Check Price is shown", exc_message)

    def test_tour_show_price(self):
        """If a configured product has `website_hide_price` disabled,
        the price is shown and the message is hidden.
        """
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
        product = session.product_id
        product.website_hide_price = False

        session_url = "/product_configurator/product/%s" % session.id
        self.start_tour(
            session_url,
            "website_product_configurator_hide_price.show_price",
            login=admin_user.login,
        )
        # There is no way to assert that a node is missing in tours,
        # so we check that the tour fails.
        with self.assertRaises(AssertionError) as ae, mute_logger(TEST_BROWSER_PATH):
            self.start_tour(
                session_url,
                "website_product_configurator_hide_price.show_message",
                login=admin_user.login,
            )
        exc_message = ae.exception.args[0]
        self.assertIn("failed at step Check Message is shown", exc_message)
