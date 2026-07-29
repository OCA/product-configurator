{
    "name": "Product Configurator Purchase",
    "version": "18.0.1.0.0",
    "category": "Generic Modules/Purchase",
    "summary": "Product configuration interface for Purchase",
    "website": "https://github.com/OCA/product-configurator",
    "license": "AGPL-3",
    "author": "Nitrokey GmbH, Odoo Community Association (OCA)",
    "depends": ["purchase", "product_configurator"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/purchase_view.xml",
    ],
    "demo": ["demo/product_template.xml"],
    "installable": True,
    "auto_install": False,
    "maintainer": "Nitrokey GmbH",
}
