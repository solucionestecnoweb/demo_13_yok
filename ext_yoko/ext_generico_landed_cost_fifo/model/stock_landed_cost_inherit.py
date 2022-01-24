# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError

class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost.lines'

    price_unit_aux = fields.Float()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_secundaria_id.id)

    @api.onchange('price_unit_aux','currency_id')
    #@api.depends('price_unit_aux','currency_id')
    def calcula_tasa(self):
        for selff in self:
            if selff.env.company.currency_id.id==selff.currency_id.id:
                pass
                selff.price_unit=selff.price_unit_aux
            else:
                lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', selff.currency_id.id),('hora','<=',selff.cost_id.date)],order='hora ASC')
                if lista_tasa:
                    for det in lista_tasa:
                        valor=selff.price_unit_aux/det.rate
                    selff.price_unit=valor


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    line_resumen  = fields.Many2many(comodel_name='stock.landed.resumen', string='Lineas')


    def _compute_monto_conversion(self):
        valor=0
        self.env.company.currency_secundaria_id.id
        for selff in self:
            if self.env.company.currency_secundaria_id.id==selff.currency_id.id:
                valor=selff.amount_total
            if self.env.company.currency_id.id==selff.currency_id.id:
                lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('name','<=',selff.date)],order='id ASC')
                if lista_tasa:
                    for det in lista_tasa:
                        valor=selff.amount_total_signed*det.rate
            selff.amount_total_signed_aux_bs=valor
            selff.amount_total_signed_bs=valor



    def compute_landed_cost(self):
        super().compute_landed_cost()
        if not self.vendor_bill_id:
            raise UserError(_('Asigne la Factura correspondiente'))
        else:
            self.vendor_bill_id.ajusta()
        total_cos_dest=self.amount_total
        self.env['stock.landed.resumen'].search([]).unlink()#costo_id
        for det in self.valuation_adjustment_lines:
            self.calculo_nuevo_cost_uni(det.product_id,total_cos_dest)
            #raise UserError(_('Hola pipi padd=%s')%nuevo_costo_unit)

    def calculo_nuevo_cost_uni(self,producto,total_cos_dest):
        if producto.categ_id.property_cost_method=="fifo":
            busca=self.env['stock.valuation.adjustment.lines'].search([('product_id','=',producto.id),('cost_id','=',self.id)])#costo_id
            #raise UserError(_('Hola pipi paaad '))
            if busca:
                costo_adicional=0
                for det in busca:
                    moneda=self.busca_moneda(det.move_id.origin)
                    moneda_compania=self.busca_moneda_company(det.move_id.origin)
                    costo_original_total=det.former_cost
                    costo_adicional=costo_adicional+det.additional_landed_cost
                    cantidad=det.quantity
                    if producto.tasa_compra>0:
                        tasa=producto.tasa_compra
                    else:
                        raise UserError(_('El producto %s no tiene tasa registrada en su compra. Vaya a la ficha del producto y coloque la ultima tasa de compra de éste')%producto.name)
                self.registra_resumen(producto,det,costo_adicional)
                self.line_resumen=self.env['stock.landed.resumen'].search([('cost_id','=',self.id)])#costo_id
                monto_unit_total=((costo_original_total+costo_adicional)/cantidad)
                if producto.standard_price<monto_unit_total:
                    if moneda==moneda_compania:
                        producto.standard_price=monto_unit_total
                        producto.standard_price_div=monto_unit_total/tasa
                    else:
                        producto.standard_price=monto_unit_total#*tasa
                        producto.standard_price_div=monto_unit_total/tasa

    def monto_tasa(self):
        valor=0
        #self.amount_total_signed_aux_bs=valor
        self.env.company.currency_secundaria_id.id
        for selff in self:
            lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('hora','<=',selff.date_approve)],order='id ASC')
            if lista_tasa:
                for det in lista_tasa:
                    valor=det.rate
        return valor

    def busca_moneda(self,origen):
        busca=self.env['purchase.order'].search([('name','=',origen)])
        if busca:
            for det in busca:
                moneda=det.currency_id.id
        return moneda

    def busca_moneda_company(self,origen):
        busca=self.env['purchase.order'].search([('name','=',origen)])
        if busca:
            for det in busca:
                moneda_company=det.company_id.currency_id.id
        return moneda_company

    def registra_resumen(self,producto,det,costo_adicional):
        #raise UserError(_('Hola pipi paaad '))
        valida=self.env['stock.landed.resumen'].search([('product_id','=',producto.id),('cost_id','=',self.id)]) #('cost_id','=',self.id)
        if not valida:
            if not producto.tasa_compra:
                tasa=1
            else:
                tasa=producto.tasa_compra
            resumen=self.env['stock.landed.resumen']
            vals = {
                'cost_id': self.id,
                'product_id': producto.id,
                'descripcion':producto.name,
                'cantidad':det.quantity,
                'costo_original':det.former_cost,
                'costo_adicional':costo_adicional,
                'costo_total':(det.former_cost+costo_adicional),
                'costo_unit_new':(det.former_cost+costo_adicional)/det.quantity,
                'costo_unit_new_div':((det.former_cost+costo_adicional)/det.quantity)/tasa,
            }
            self.line_resumen = resumen.create(vals)


        #raise UserError(_('Hola pipi paaad 2=%s')%busca)

class StockLandedResumen(models.Model):
    _name = 'stock.landed.resumen'

    cost_id=fields.Many2one('stock.landed.cost', 'Currency')
    product_id=fields.Many2one('product_template')
    descripcion=fields.Char()
    cantidad=fields.Float()
    costo_original=fields.Float()
    costo_adicional=fields.Float()
    costo_total=fields.Float()
    costo_unit_new=fields.Float()
    costo_unit_new_div=fields.Float()
    company_id = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id.id)
    currency_company_id=fields.Many2one('res.currency',default=lambda self: self.env.company.currency_id.id)
    currency_company_secundaria_id=fields.Many2one('res.currency',default=lambda self: self.env.company.currency_secundaria_id.id)

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'
    fecha = fields.Datetime()

    def _compute_monto_conversion(self):
        valor=0
        #self.amount_total_signed_aux_bs=valor
        self.env.company.currency_secundaria_id.id
        for selff in self:
            lista_tasa = selff.env['res.currency.rate'].search([('currency_id', '=', self.env.company.currency_secundaria_id.id),('hora','<=',selff.fecha)],order='id ASC')
            if lista_tasa:
                for det in lista_tasa:
                    valor=selff.value*det.rate
            selff.amount_total_signed_aux=valor

class Picking(models.Model):
    _inherit = "stock.picking"
    #date_done = fields.Datetime('Date of Transfer',readonly=False, help="Date at which the transfer has been processed or cancelled.")

    def action_done(self):
       
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            if pick.owner_id:
                pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
                pick.move_line_ids.write({'owner_id': pick.owner_id.id})

            
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'description_picking': ops.description_picking,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                    'picking_type_id': pick.picking_type_id.id,
                                                    'restrict_partner_id': pick.owner_id.id,
                                                    'company_id': pick.company_id.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': self.scheduled_date})
        self._send_confirmation_email()
        self.ajustar_valor_inventario()
        return True

    def ajustar_valor_inventario(self):
        sm = self.env['stock.move'].search([('picking_id', '=', self.id)])
        if sm:
            for dsm in sm:
                p=dsm.product_id.id
                cant=dsm.quantity_done
                purchase=self.env['purchase.order'].search([('name', '=', self.origin)])
                for dp in purchase:
                    line_purchase=self.env['purchase.order.line'].search([('order_id', '=', dp.id),('product_id','=',dsm.product_id.id)])
                    for linea in line_purchase:
                        precio_unitario=linea.price_unit
                        cantidad=linea.product_qty
                        layerstock=self.env['stock.valuation.layer'].search([('stock_move_id', '=',dsm.id)])
                        layerstock.write({
                            'unit_cost':linea.price_unit*self.busca_tasa(dp.currency_id.id),
                            'value':linea.product_qty*linea.price_unit*self.busca_tasa(dp.currency_id.id),
                            'remaining_value':linea.product_qty*linea.price_unit*self.busca_tasa(dp.currency_id.id),
                            'quantity':linea.product_qty,
                            'fecha':self.scheduled_date,
                            })


    #@api.onchange('state')
    """@api.depends('state')
    def recalcula(self):
        raise UserError(_('Hola pipi paaad'))"""


    def busca_tasa(self,id_currency):
        valor=1
        lista_tasa = self.env['res.currency.rate'].search([('currency_id', '=', id_currency),('name','<=',self.scheduled_date)],order='id ASC')
        if lista_tasa:
            for tas in lista_tasa:
                valor=(1/tas.rate)
        return valor

