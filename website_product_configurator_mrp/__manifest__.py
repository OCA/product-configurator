# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Configurator Manufacturing",
    "version": "14.0.1.0.0",
    "category": "Website",
    "summary": "Website integration of MRP",
    "author": "Pledra, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": ["product_configurator_mrp", "website_product_configurator"],
    "data": ["views/templates.xml", "views/assets.xml"],
    "application": True,
    "installable": True,
    "development_status": "Beta",
    "maintainers": ["PCatinean"],
    "auto_install": False,
}
