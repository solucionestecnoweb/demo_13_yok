# -*- coding: utf-8 -*-


from odoo import api, fields, models, _




class ResCompany(models.Model):
    _inherit = 'res.company'

    logo_factura = fields.Binary(string='Logo Factura', help='Logo de la factura electronica')