from datetime import timedelta

from odoo import api, fields, models


class ProductConfigSession(models.Model):
    _inherit = "product.config.session"

    def remove_inactive_config_sessions(self):
        check_date = fields.Datetime.from_string(fields.Datetime.now()) - timedelta(
            days=3
        )
        sessions_to_remove = self.search(
            [("write_date", "<", fields.Datetime.to_string(check_date))]
        )
        if sessions_to_remove:
            sessions_to_remove.unlink()
