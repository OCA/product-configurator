{
    "name": "Product Configurator MRP Quantity",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Configuration for adding quantity in product configurator.",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": ["product_configurator", "product_configurator_mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/product_attribute_view.xml",
        "wizard/product_configurator_view.xml",
        "views/product_config_view.xml",
        "views/attribute_value_qty_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            '/product_configurator_mrp_quantity/static/src/xml/web_inner_group.xml',
            '/product_configurator_mrp_quantity/static/src/scss/from_group_scss.scss'
        ]
    },
    "images": ["static/description/cover.png"],
    "development_status": "Beta",
    "uninstall_hook": "uninstall_hook",
    "maintainer": "Open Source Integrators",
    "installable": True,
    "auto_install": False,
}
