{
    'name': "Modulo de gastos adaptado con anticipos e inclucion libro en libro de compra",

    'summary': """Modulo de gastos adaptado con anticipos e inclucion libro en libro de compra""",

    'description': """
       Modulo de gastos adaptado con anticipos e inclucion libro en libro de compra

    """,
    'version': '2.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense','account','libro_resumen_alicuota','libro_compras'],

    # always loaded
    'data': [
    'vista/hr_expense_inherit.xml',
    'vista/hr_expense_anticipo.xml',
    'security/ir.model.access.csv',
    #'date/date_plazo_meta.xml',
    ],
    'application': True,
}
