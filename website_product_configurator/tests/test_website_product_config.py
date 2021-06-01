import odoo.tests


@odoo.tests.common.tagged("post_install", "-at_install")
class TestUi(odoo.tests.HttpCase):
    def test_01_admin_config_tour(self):
        self.start_tour(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('config')",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.config.ready",
            login="admin",
        )

    def test_02_demo_config_tour(self):
        self.start_tour(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('config')",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.config.ready",
            login="demo",
        )
