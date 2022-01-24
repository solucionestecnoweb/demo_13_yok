# -*- coding: utf-8 -*-
{
    'name': "campos account move",

    'summary': """campos account move""",

    'description': """
       campos account move
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'campos account move',

    # any module necessary for this one to work correctly
    'depends': ['product','base', 'account','sale','purchase','stock'],

    # always loaded
    'data': [
        #'vista/sale_order_inherit.xml',
        #'vista/stock_piking_inherit.xml',
        #'security/ir.model.access.csv',
    ],
    'application': True,
}
