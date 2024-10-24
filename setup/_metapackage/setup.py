import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-product-configurator",
    description="Meta package for oca-product-configurator Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-product_configurator>=16.0dev,<16.1dev',
        'odoo-addon-product_configurator_mrp>=16.0dev,<16.1dev',
        'odoo-addon-product_configurator_sale>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
