# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Configurator Sale",
    "version": "14.0.1.1.3",
    "category": "Generic Modules/Sale",
    "summary": "Product configuration interface modules for Sale",
    "author": "Pledra, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": ["sale_management", "product_configurator"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/sale_view.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
}
