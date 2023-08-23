# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Configurator for Stock",
    "version": "14.0.1.1.0",
    "category": "Generic Modules/Stock",
    "summary": "Product configuration interface module for Stock",
    "author": "Pledra, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": ["stock", "product_configurator"],
    "data": [
        "data/menu_product.xml",
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        "views/stock_move_view.xml",
        "views/product_view.xml",
    ],
    "demo": ["demo/product_template.xml"],
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
    "auto_install": False,
}
