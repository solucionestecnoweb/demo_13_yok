# -*- coding: utf-8 -*-
{
    'name': "Campo Nro de Control Manual factura Cliente",

    'summary': """Campo Nro de Control Manual factura Cliente """,

    'description': """
       v 
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'Campo Nro de Control Manual factura Cliente',

    # any module necessary for this one to work correctly
    'depends': ['product','base', 'vat_retention','l10n_ve_fiscal_requirements','ext_yoko_formato_factura_nd_nc'],

    # always loaded
    'data': [
        'vista/vista_account_move_inherit.xml',
    ],
    'application': True,
}
