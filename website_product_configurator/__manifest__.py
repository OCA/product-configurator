{
    "name": "Website Product Configurator",
    "version": "16.0.1.0.0",
    "summary": """Configure products in e-shop""",
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
        "data/ir_config_parameter_data.xml",
        "data/config_form_templates.xml",
        "data/cron.xml",
        "views/product_view.xml",
        "views/templates.xml",
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_product_configurator/static/src/js/config_form.js",
            "website_product_configurator/static/src/js/variant_mixin.js",
            "website_product_configurator/static/src/js/website_sale.esm.js",
            "website_product_configurator/static/src/js/website_config_tour.js",
            "website_product_configurator/static/src/scss/config_form.scss",
            "website_product_configurator/static/src/scss/tooltip.scss",
        ],
        "web.assets_tests": [
            "website_product_configurator/static/tests/tours/custom_values.esm.js",
            "website_product_configurator/static/tests/tours/reconfigure_cart_line.esm.js",
        ],
    },
    "demo": ["demo/product_template_demo.xml"],
    "images": ["static/description/cover.png"],
    "application": True,
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
}
