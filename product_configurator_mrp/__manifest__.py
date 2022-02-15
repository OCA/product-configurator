# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Configurator Manufacturing",
    "version": "14.0.1.2.3",
    "category": "Manufacturing",
    "summary": "BOM Support for configurable products",
    "author": "Pledra, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": ["mrp", "product_configurator"],
    "data": [
        "data/menu_product.xml",
        "views/assets.xml",
        "views/mrp_view.xml",
        "security/configurator_security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/product_template.xml"],
    "qweb": ["static/src/xml/mrp_production_views.xml"],
    "installable": True,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
}
