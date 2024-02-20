{
    'name': 'Product Configurator Sale',
    'version': '11.0.1.0.3',
    'category': 'Generic Modules/Sale',
    'summary': 'Product configuration interface modules for Sale',
    'author': 'Pledra',
    'license': 'AGPL-3',
    'website': 'http://www.pledra.com/',
    'depends': ['sale_management', 'product_configurator'],
    "data": [
        'data/menu_product.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        'demo/res_partner_demo.xml',
    ],
    'images': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
