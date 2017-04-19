# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2013, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class sale_order(Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    _columns = {
        'voucher_logo': fields.selection([('dc', 'Destination Cuba'), 
                                          ('cc', 'Captivating Cuba'),
                                          ('cd', 'Destino Cuba'),
                                          ('htg', 'Hovis Travel Group')],
                                         'Voucher Logo'),
    }
    
    _defaults = {
                 'voucher_logo': 'dc'
                 }

    # def action_button_confirm(self, cr, uid, ids, context=None):
    #     for order in self.browse(cr, uid, ids, context):
    #         for line in order.order_line:
    #             if line.price_unit == 0:
    #                 raise except_orm(_('Operation Canceled'), _('Please verify that price unit lines must be distinct of zero.'))
    #     return super(sale_order, self).action_button_confirm(cr, uid, ids, context)


class sale_order_line(Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    # def get_margin_days(self, cr, uid, params, context=None):
    #     '''
    #     The number of days of the service countable for apply a per day margin.
    #     Redefining the travel_core function
    #     '''
    #     if not params.get('start_date', False) or not params.get('end_date', False):
    #         raise Warning(_('Please introduce the range of date.'))
    #     return super(sale_order_line, self).get_margin_days(cr, uid, params, context)

    def onchange_category(self, cr, uid, ids, category_id, context=None):
        if not category_id:
            res = {}
            order_line = self.browse(cr, uid, ids)
            if order_line:
                if not order_line.start_date and not order_line.end_date:
                    res['value'] = {'start_date': context.get('date_order', False), 'end_date': context.get('end_date', False)}
            else:
                res['value'] = {'start_date': context.get('date_order', False), 'end_date': context.get('end_date', False)}
            return res
        else:
            return super(sale_order_line, self).onchange_category(cr, uid, ids, category_id, context)

    def product_price(self, cr, uid, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                      supplier_id=False,
                      lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,
                      category='', end_date_order='', adults=0, context=None):
        context = context or {}
        context['params'] = {'category': category,
                             'start_date': date_order,
                             'end_date': end_date_order,
                             'adults': adults}
        lang = lang or context.get('lang', False)
        if not partner_id:
            raise except_orm(_('No Customer Defined !'),
                                 _('Before choosing a product,\n select a customer in the sales form.'))
        # warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        supplier_id = supplier_id or False
        params = context.get('params', {})
        context = {
            'lang': lang,
            'partner_id': partner_id,
            'supplier_id': supplier_id,
            'params': params
        }
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            raise except_orm(_('No Product Defined !'), _('Please set of product.'))
        if not date_order:
            date_order = time.strftime(DF)

        result = {}
        # warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product,
                                         context=context_partner)
        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        afp = self.pool.get('account.fiscal.position')
        fpos = fiscal_position and afp.browse(cr, uid, fiscal_position) or False
        if update_tax:
            result['tax_id'] = afp.map_tax(cr, uid, fpos, product_obj.taxes_id)
        if not flag:
            pp = self.pool.get('product.product')
            result['name'] = pp.name_get(cr, uid, [product_obj.id],
                                         context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n' + product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                      [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                      [('category_id', '=', uos_category_id)]}
        elif uos and not uom:
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom:
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight

        if not uom2:
            uom2 = product_obj.uom_id

        if not pricelist:
            raise except_orm(_('No pricelist Defined !'), _('Please set of pricelist.'))
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        'supplier_id': supplier_id,
                        'params': params
                        })[pricelist]
            sale_currency_id = self.pool.get('product.pricelist').read(cr, uid, [pricelist], ['currency_id'])[0]['currency_id'][0]
            cost_currency = self.get_supplierinfo(cr, uid, product, supplier_id)
            if cost_currency and cost_currency.currency_cost_id:
                cost_currency_id = cost_currency.currency_cost_id.id
            else:
                cost_currency_id = self.default_currency_cost(cr, uid, context)

            if sale_currency_id != cost_currency_id:
                cr_obj = self.pool.get('res.currency')
                price = cr_obj.compute(cr, uid, cost_currency_id, sale_currency_id, price, round=False, context=context)

            cost_price, currency_cost_id = self.show_cost_price(cr, uid, result, product, qty, partner_id, uom,
                                                                date_order, supplier_id, params, pricelist, context)
            result.update({'price_unit_cost': cost_price, 'currency_cost_id': currency_cost_id})

        return price, cost_price, currency_cost_id
