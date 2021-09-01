{
    "name": "Product Configurator Purchase",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Purchase",
    "summary": "Product configuration interface for Purchase",
    "author": "Pledra, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": ["purchase", "product_configurator"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/purchase_view.xml",
    ],
    "demo": ["demo/product_template.xml"],
    "images": [],
    "test": [],
    "installable": False,
    "auto_install": False,
    "development_status": "Beta",
    "maintainers": ["pcatinean"],
}
