from odoo.tests.common import TransactionCase


class TestResConfigSettings(TransactionCase):
    def setUp(self):
        super(TestResConfigSettings, self).setUp()
        self.ResConfigObj = self.env["res.config.settings"]
        self.res_config = self.ResConfigObj.create(
            {
                "website_tmpl_id": self.env.ref(
                    "website_product_configurator.config_form_base"
                ).id,
            }
        )
        self.res_config_select = self.ResConfigObj.create(
            {
                "website_tmpl_id": self.env.ref(
                    "website_product_configurator.config_form_select"
                ).id,
            }
        )
        self.res_config_select.set_values()

    def test_xml_id_to_record_id(self):
        website_tmpl_id = self.res_config.xml_id_to_record_id(False)
        self.assertFalse(website_tmpl_id, "xml_id is set")
        website_tmpl_id = self.res_config.xml_id_to_record_id(
            self.res_config.website_tmpl_id.xml_id
        )

        self.assertEqual(
            website_tmpl_id,
            False,
        )
        website_tmpl_id_select = self.res_config_select.xml_id_to_record_id(
            self.res_config_select.website_tmpl_id.xml_id
        )
        self.assertTrue(website_tmpl_id_select, "website_tmpl_id_select is not set")
