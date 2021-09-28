# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class ResPartner(models.Model):
    _inherit = 'res.partner'

    canal=fields.Selection([('BV', 'B2B (VIP)'),('BO', 'B2B OFICINA')],string="Canal")
    canales=fields.Many2one('res.canal')
    mercado=fields.Many2one('res.mercado')
    vendedor=fields.Selection([('BV', 'B2B (VIP)'),('BO', 'B2B OFICINA')],string="Vendedor")
    vendedores=fields.Many2one('res.vendedor')
    formato=fields.Many2one('res.formato')
    responsable=fields.Char(string="Responsable")

    istagram=fields.Char(string="Instagram")
    activo=fields.Boolean(string="Activo")
    tipologia=fields.Many2one('res.tipologia')
    tienda=fields.Char(string="Tienda")
    deposito=fields.Char(string="Deposito")
    zona=fields.Char(string="Zona")
    razon=fields.Char(string="Razon Social")
   
    #uni_neg_id = fields.Many2one('stock.unidad.negocio')

class ModeloCanal(models.Model):
    _name = 'res.canal'

    name=fields.Char()

class ModeloVendedor(models.Model):
    _name = 'res.vendedor'

    name=fields.Char()

class ModeloMercado(models.Model):
    _name = 'res.mercado'

    name=fields.Char()

class TipoTipologia(models.Model):
    _name = 'res.tipologia'

    name=fields.Char()

class ResFormato(models.Model):
    _name = 'res.formato'

    name=fields.Char()
        