# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        super().action_post()
        self.ajusta()

    def ajusta(self):
        tasa=abs(self.amount_total_signed/self.amount_total)
        #raise UserError(_('Hola pipi padd yaya=%s')%tasa)
        moneda=self.currency_id.id
        moneda_compania=self.company_id.currency_id.id
        for det_line in self.invoice_line_ids:
            #metodo_costo=det_line.product_id.product_tmpl_id.categ_id.property_cost_method
            metodo_costo=det_line.product_id.categ_id.property_cost_method
            valor_costo_unitario=det_line.price_unit
            if metodo_costo=="fifo":
                if moneda==moneda_compania:
                    #if valor_costo_unitario>det_line.product_id.standard_price:
                    det_line.product_id.standard_price=valor_costo_unitario
                    det_line.product_id.tasa_compra=(1/self.monto_conversion2())#tasa
                    det_line.product_id.standard_price_div=valor_costo_unitario*self.monto_conversion2()
                    det_line.product_id.standard_price_fob=valor_costo_unitario
                    det_line.product_id.standard_price_div_fob=valor_costo_unitario*self.monto_conversion2()
                else:
                    #if (valor_costo_unitario*tasa)>det_line.product_id.standard_price:
                    det_line.product_id.standard_price=valor_costo_unitario*tasa
                    det_line.product_id.tasa_compra=tasa
                    det_line.product_id.standard_price_div=valor_costo_unitario
                    det_line.product_id.standard_price_fob=valor_costo_unitario*tasa
                    det_line.product_id.standard_price_div_fob=valor_costo_unitario

    def monto_conversion2(self):
        valor=0
        #self.amount_total_signed_aux_bs=valor
        self.env.company.currency_secundaria_id.id
        for selff in self:
            lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('hora','<=',selff.date)],order='id ASC')
            if lista_tasa:
                for det in lista_tasa:
                    valor=det.rate
        return valor

class SaleOrder(models.Model):
    _inherit = 'purchase.order'


    def button_confirm(self):
        super().button_confirm()
        #raise UserError(_('Hola pipi padd='))
        tasa=(1/self.currency_rate)
        moneda=self.currency_id.id
        moneda_compania=self.company_id.currency_id.id
        for det_line in self.order_line:
            #metodo_costo=det_line.product_id.product_tmpl_id.categ_id.property_cost_method
            metodo_costo=det_line.product_id.categ_id.property_cost_method
            valor_costo_unitario=det_line.price_unit
            if metodo_costo=="fifo":
                if moneda==moneda_compania:
                    if valor_costo_unitario>det_line.product_id.standard_price:
                        det_line.product_id.standard_price=valor_costo_unitario
                        det_line.product_id.tasa_compra=(1/self.monto_conversion())#tasa
                        det_line.product_id.standard_price_div=valor_costo_unitario*self.monto_conversion()
                        det_line.product_id.standard_price_fob=valor_costo_unitario
                        det_line.product_id.standard_price_div_fob=valor_costo_unitario*self.monto_conversion()
                else:
                    if (valor_costo_unitario*tasa)>det_line.product_id.standard_price:
                        det_line.product_id.standard_price=valor_costo_unitario*tasa
                        det_line.product_id.tasa_compra=tasa
                        det_line.product_id.standard_price_div=valor_costo_unitario
                        det_line.product_id.standard_price_fob=valor_costo_unitario*tasa
                        det_line.product_id.standard_price_div_fob=valor_costo_unitario
            #raise UserError(_('producto=%s')%metodo_costo)

    def monto_conversion(self):
        valor=0
        #self.amount_total_signed_aux_bs=valor
        self.env.company.currency_secundaria_id.id
        for selff in self:
            lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('hora','<=',selff.date_approve)],order='id ASC')
            if lista_tasa:
                for det in lista_tasa:
                    valor=det.rate
        return valor

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price', default=lambda self: self.product_id.standard_price)

class StockPikingg(models.Model):
    _inherit = 'stock.picking'

    def monto_conversion(self):
        valor=0
        #self.amount_total_signed_aux_bs=valor
        self.env.company.currency_secundaria_id.id
        for selff in self:
            lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('hora','<=',selff.scheduled_date)],order='id ASC')
            if lista_tasa:
                for det in lista_tasa:
                    valor=det.rate_real
        return valor

    def action_done(self):
        res=super(StockPikingg,self).action_done()
        tasa=self.monto_conversion()
        moneda_compania=self.company_id.currency_id.id
        lista_orden = self.env['purchase.order'].search([('name', '=', self.origin)])
        if lista_orden:
            for dett in lista_orden:
                moneda=dett.currency_id.id
                for det_line in dett.order_line:
                    metodo_costo=det_line.product_id.categ_id.property_cost_method
                    valor_costo_unitario=det_line.price_unit
                    if metodo_costo=="fifo":
                        if moneda==moneda_compania:
                            if valor_costo_unitario>det_line.product_id.standard_price:
                                #raise UserError(_('Hola pipi paaad '))
                                det_line.product_id.standard_price=valor_costo_unitario
                                det_line.product_id.tasa_compra=(1/self.monto_conversion())
                                det_line.product_id.standard_price_div=valor_costo_unitario*self.monto_conversion()
                                det_line.product_id.standard_price_fob=valor_costo_unitario
                                det_line.product_id.standard_price_div_fob=valor_costo_unitario*self.monto_conversion()
                        else:
                            if (valor_costo_unitario*tasa)>det_line.product_id.standard_price:
                                #raise UserError(_('Hola pipi paaad 2'))
                                det_line.product_id.standard_price=valor_costo_unitario*tasa
                                det_line.product_id.tasa_compra=tasa
                                det_line.product_id.standard_price_div=valor_costo_unitario
                                det_line.product_id.standard_price_fob=valor_costo_unitario*tasa
                                det_line.product_id.standard_price_div_fob=valor_costo_unitario
        