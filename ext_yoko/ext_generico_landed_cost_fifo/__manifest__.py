# -*- coding: utf-8 -*-
{
    'name': "Metodo de costo del producto por FIFO y trae ultimo costo o costo mas alto",

    'summary': """Metodo de costo del producto por FIFO y trae ultimo costo o costo mas alto""",

    'description': """
       Metodo de costo del producto por FIFO y trae ultimo costo o costo mas alto
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'Metodo de costo del producto por FIFO y trae ultimo costo o costo mas alto',

    # any module necessary for this one to work correctly
    'depends': ['product','base', 'account','sale','purchase','stock','product','stock_landed_costs',
    'ext_doble_aprovacion_ordenes_venta_compra',
    'l10n_ve_asientos_bs_$_inventario_fabricacion',],

    # always loaded
    'data': [
        'vista/product_template_inherit.xml',
        'vista/landed_cost_inherit.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
