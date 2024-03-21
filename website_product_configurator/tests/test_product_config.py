from ..tests.test_website_product_configurator_values import (
    TestProductConfiguratorValues,
)


class TestProductConfigStepLine(TestProductConfiguratorValues):
    def test_get_website_template(self):
        self.configStepLine.write(
            {
                "website_tmpl_id": self.env.ref(
                    "website_product_configurator.config_form_radio"
                ).id,
            }
        )
        view_id = self.configStepLine.get_website_template()
        self.assertEqual(
            view_id,
            "website_product_configurator.config_form_radio",
            "We do not return the correct view_id",
        )
        self.configStepLine.write({"website_tmpl_id": False})
        view_id2 = self.configStepLine.get_website_template()
        self.assertEqual(
            view_id2,
            "website_product_configurator.config_form_select",
            "We do not return the correct view_id",
        )

        # set template id false
        self.env["ir.config_parameter"].sudo().set_param(
            "product_configurator.default_configuration_step_website_view_id", False
        )
        dafault_template_xml_id = self.configStepLine.get_website_template()
        self.assertEqual(
            dafault_template_xml_id,
            "website_product_configurator.config_form_select",
            "Default Template xml id is not set.",
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
