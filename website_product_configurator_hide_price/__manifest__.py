#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hide price in Website Product Configurator",
    "summary": "Hide price in Product Configurator",
    "category": "website",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "author": "Aion Tech, Odoo Community Association (OCA)",
    "maintainers": [
        "SirAionTech",
    ],
    "depends": [
        "website_product_configurator",
        "website_sale_hide_price",
    ],
    "auto_install": True,
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "website_product_configurator_hide_price/static/tests/tours/show_message.esm.js",
            "website_product_configurator_hide_price/static/tests/tours/show_price.esm.js",
        ],
    },
}
