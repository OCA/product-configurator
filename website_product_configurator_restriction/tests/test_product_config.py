from ..tests.test_website_product_configurator_values import (
    TestProductConfiguratorValues,
)


class TestProductConfig(TestProductConfiguratorValues):
    def test_remove_inactive_config_sessions(self):
        self.session_id.remove_inactive_config_sessions()
        sessions_to_remove = self.productConfigSession.search(
            [
                (
                    "id",
                    "=",
                    self.session_id.id,
                )
            ]
        )
        self.assertFalse(sessions_to_remove, "session_id is not deleted")
        self.session_id2.remove_inactive_config_sessions()
        sessions_to_remove2 = self.productConfigSession.search(
            [
                (
                    "id",
                    "=",
                    self.session_id2.id,
                )
            ]
        )
        self.assertTrue(sessions_to_remove2, "session_id does not deleted")
