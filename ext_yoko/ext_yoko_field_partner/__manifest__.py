# -*- coding: utf-8 -*-
{
    'name': "Campos adicionales en ficha de clientes",

    'summary': """Campos adicionales en ficha clientes Inversiones_081213""",

    'description': """
       Campos adicionales en ficha clientes Inversiones_081213
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'Campos adicionales en ficha cliente Inversiones_081213',

    # any module necessary for this one to work correctly
    'depends': ['product','base', 'stock','sale','purchase'],

    # always loaded
    'data': [
        'res_partner_inherit.xml',
        'view_add.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
}
