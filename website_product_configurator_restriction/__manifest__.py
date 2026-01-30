{
    "name": "Website Product Configurator Restriction",
    "version": "18.0.1.0.0",
    "summary": """Website configure products restriction in e-shop""",
    "author": "Pledra, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "category": "website",
    "depends": [
        "website_sale",
        "product_configurator",
        "product_configurator_sale",
    ],
    "data": [
        "security/configurator_security.xml",
        "data/data_file.xml",
    ],
    "images": ["static/description/cover.png"],
    "application": True,
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
    "assets": {
        "web.assets_frontend": [
            "website_product_configurator_restriction/static/src/js/variant_mixin.js",
            "website_product_configurator_restriction/static/src/js/website_sale.js",
        ],
        # "web.assets_tests": [
        #     "website_product_configurator_restriction/static/tests/tours/**/*"
        # ],
    },
}
