# Copyright 2025 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product Configurator Sale - Create product variant from custom value",
    "version": "16.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Allow to create variant for custom values for configurable products.",
    "author": "Aion Tech, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/product-configurator",
    "depends": [
        "product_configurator_sale",
        "product_attribute_custom_value_variant",
    ],
    "auto_install": True,
    "data": [
        "views/product_attribute_views.xml",
    ],
}
