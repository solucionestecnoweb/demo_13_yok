# -*- coding: utf-8 -*-

{
        'name': 'Product Moves invoice',
        'version': '0.1',
        'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
        'summary': '',
        'description': """""",
        'category': 'Accounting/Accounting',
        'website': '',
        'images': [],
        'depends': [
            'stock',
            'sale_stock',
            'l10n_ve_formato_factura_nd_nc',
            ],
        'data': [
            'views/stock_move_line_views.xml',
            'views/stock_picking_views.xml'
                 ],
        'installable': True,
        'application': False,
        'auto_install': False,
                      
}
