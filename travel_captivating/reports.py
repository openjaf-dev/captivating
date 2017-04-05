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

import datetime as dt

from openerp.osv import fields, osv
from openerp.osv.orm import Model
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _


class sale_order_line(Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    
    def _get_related_order_lines(self, cr, uid, ids, context=None):
        # Get all order_lines belonging to same sale_order 
        res = {}
        for ol1 in self.browse(cr, uid, ids, context=context):
            for ol2 in ol1.order_id.order_line:
                res[ol2.id] = True
                
        return res.keys()  
        
    def _get_hotel_from(self, cr, uid, ids, fields, args, context=None):        
        return self.get_hotel_match(cr, uid, ids, 'end_date', context)
        
    def _get_hotel_to(self, cr, uid, ids, fields, args, context=None):          
        return self.get_hotel_match(cr, uid, ids, 'start_date', context)
    
    def _compute_start_end(self, cr, uid, ids, fields, args, context=None):
        
        result = {} 
          
        hotel = self.pool.get('product.hotel')
        sale = self.pool.get('sale.order')
        order_line = self.pool.get('sale.order.line')
        
        for obj in self.browse(cr, uid, ids, context):
            if obj.product_id.categ_id.name == 'Transfer':
                sale_obj = sale.browse(cr, uid, obj.order_id.id)
                for order_line_obj in sale_obj.order_line:
                    product = order_line_obj.product_id
                    if product.categ_id.name == 'Hotel':
                        if order_line_obj.end_date == obj.start_date:
                            result.setdefault(obj.id, {'hotel_from': product.name, 'hotel_to': ''})
                            result[obj.id]['hotel_from'] = product.name   
                        elif order_line_obj.start_date == obj.start_date:
                            result.setdefault(obj.id, {'hotel_from': '', 'hotel_to': product.name})
                            result[obj.id]['hotel_to'] = product.name     
          
        return result    
    
    _columns = {             
        'hotel_from':
            fields.function(_compute_start_end, method=True, type='char',
                            string='Hotel from', size=128,
                            store = {'sale.order.line': (_get_related_order_lines, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),             
        'hotel_to':
            fields.function(_compute_start_end, method=True, type='char',
                            string='Hotel to', size=128,
                            store = {'sale.order.line': (_get_related_order_lines, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to')
                   
        
    }


class sale_order(Model):
    _name = 'sale.order'
    _inherit = 'sale.order'   
     
    def _get_related_orders(self, cr, uid, ids, context=None):
        # Get all order_lines belonging to same sale_order 
        res = {}
        order_lines = self.pool.get('sale.order.line').browse(cr, uid, ids, context=context)
        for ol in order_lines:
                res[ol.order_id.id] = True
                
        return res.keys()  
    
    def _get_start_transfer(self, cr, uid, ids, fields, args, context=None):        
        return self.get_product_match(cr, uid, ids, 'start_date', 'date_order', 'Transfer', context)
        
    def _get_end_transfer(self, cr, uid, ids, fields, args, context=None):          
        return self.get_product_match(cr, uid, ids, 'start_date', 'end_date', 'Transfer', context)
    
    def _get_start_hotel(self, cr, uid, ids, fields, args, context=None):        
        return self.get_product_match(cr, uid, ids, 'start_date', 'date_order', 'Hotel', context)
        
    def _get_end_hotel(self, cr, uid, ids, fields, args, context=None):          
        return self.get_product_match(cr, uid, ids, 'end_date', 'end_date', 'Hotel', context)
         
    def _compute_start_end(self, cr, uid, ids, fields, args, context=None):        
        result = {} 
                
        for order_obj in self.browse(cr, uid, ids, context):
            order_lines = order_obj.order_line
            for i in range(0, len(order_obj.order_line)-1):
                for j in range(i+1, len(order_obj.order_line)):
                    hotel = None
                    transfer = None
                    def get_product(product_name):
                        for idx in [i,j]:
                            if order_lines[idx].product_id.categ_id.name == product_name:
                                return order_lines[idx]
                        return None
                    hotel = get_product('Hotel')
                    transfer = get_product('Transfer')
                    if hotel and transfer:
                        transfer_str = transfer.name + " (" + str(transfer.reservation_number) + ")"
                        hotel_str = hotel.name + " (" + str(hotel.reservation_number) + ")"
                        if order_obj.date_order == transfer.start_date:
                            result.setdefault(order_obj.id, {'start_transfer': transfer_str, 
                                                       'end_transfer': '',
                                                       'start_hotel': '',
                                                       'end_hotel': ''})
                            result[order_obj.id]['start_transfer'] = transfer_str
                        if order_obj.date_order == hotel.start_date:  
                            result.setdefault(order_obj.id, {'start_transfer': '', 
                                                       'end_transfer': '',
                                                       'start_hotel': hotel_str,
                                                       'end_hotel': ''})  
                            result[order_obj.id]['start_hotel'] = hotel_str                        
                        if order_obj.end_date == transfer.start_date:
                            result.setdefault(order_obj.id, {'start_transfer': '', 
                                                       'end_transfer': transfer_str,
                                                       'start_hotel': '',
                                                       'end_hotel': ''})
                            result[order_obj.id]['end_transfer'] = transfer_str
                        if order_obj.end_date == hotel.end_date:  
                            result.setdefault(order_obj.id, {'start_transfer': '', 
                                                       'end_transfer': '',
                                                       'start_hotel': '',
                                                       'end_hotel': hotel_str})   
                            result[order_obj.id]['end_hotel'] = hotel_str
                            
        return result   
                       
    _columns = {             
        'start_transfer':
            fields.function(_compute_start_end, method=True, type='char',
                            string='Start Transfer', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),             
        'end_transfer':
            fields.function(_compute_start_end, method=True, type='char',
                            string='End Transfer', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),
        'start_hotel':      
            fields.function(_compute_start_end, method=True, type='char',
                            string='Start Hotel', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),     
        'end_hotel':      
            fields.function(_compute_start_end, method=True, type='char',
                            string='End Hotel', size=128,
                            store = {'sale.order.line': (_get_related_orders, 
                                                         ['start_date', 
                                                          'end_date',
                                                          'reservation_number',
                                                          'name'], 
                                                         10)},
                            multi = 'from_to'),     
        
    }


class res_company(Model):
    _name = 'res.company'
    _inherit = 'res.company'

    _columns = {
        'group_supplier_invoice': fields.boolean('Group Supplier by Invoice')
                }

    _defaults = {
        'group_supplier_invoice': True,
    }


class account_invoice(Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def not_group_by_supplier(self, cr, uid, invoice, vals, context):
        sol_obj = self.pool.get('sale.order.line')
        sc_obj = self.pool.get('sale.context')
        lines_by_supplier = {}
        for line in invoice.invoice_line:
            to_search = [('order_id.name', '=', line.origin),
                         ('product_id', '=', line.product_id.id)]
            sol_ids = sol_obj.search(cr, uid, to_search, context=context)
            if sol_ids:
                order_line = sol_obj.browse(cr, uid, sol_ids[0], context)
                supplier = sc_obj.get_supplier(order_line)
                data = {'invoice_line': line, 'sale_line': order_line}
                lines_by_supplier[supplier] = [data]

                currency_id = order_line.currency_cost_id.id
                data = vals.copy()
                data.update({
                    'partner_id': supplier.id,
                    'account_id': supplier.property_account_payable.id,
                    'currency_id': currency_id,
                    'invoice_line': []
                })

                cost_price = order_line.price_unit_cost
                line_vals = {
                    'name': line.product_id.name,
                    'origin': line.invoice_id.number,
                    'product_id': line.product_id.id,
                    'account_id': line.product_id.categ_id.property_account_expense_categ.id,
                    'quantity': line.quantity,
                    'discount': line.discount,
                    'price_unit': cost_price,
                    'sol_start_date': order_line.start_date,
                    'sol_end_date': order_line.end_date,
                    'sol_confirmation': order_line.reservation_number
                }
                so_client_order_ref = order_line.order_id.client_order_ref
                so_lead_name = order_line.order_id.lead_name

                data['invoice_line'].append((0, 0, line_vals))

                data['so_client_order_ref'] = so_client_order_ref
                data['so_lead_name'] = so_lead_name
                inv_id = self.create(cr, uid, data, context)

    def generate_supplier_invoices(self, cr, uid, inv_id, context=None):
        invoice = self.browse(cr, uid, inv_id, context)
        company_id = invoice.company_id
        journal_id = self.get_purchase_journal(cr, uid, company_id.id, context)
        vals = {
            'type': 'in_invoice',
            'state': 'draft',
            'journal_id': journal_id,
            'date_invoice': invoice.date_invoice,
            'period_id': invoice.period_id.id,
            'user_id': invoice.user_id.id,
            'company_id': company_id.id,
            'origin': invoice.origin,
            'comment': 'Generated from customer invoice ' + invoice.origin
        }

        if company_id.group_supplier_invoice:
            lines_by_supplier = self.group_by_supplier(cr, uid, invoice, context)

            for s, lines in lines_by_supplier.items():
                currency_id = lines[0]['sale_line'].currency_cost_id.id
                data = vals.copy()
                data.update({
                    'partner_id': s.id,
                    'account_id': s.property_account_payable.id,
                    'currency_id': currency_id,
                    'invoice_line': []
                })
                for l in lines:
                    sl = l['sale_line']
                    il = l['invoice_line']
                    cost_price = sl.price_unit_cost
                    line_vals = {
                        'name': il.product_id.name,
                        'origin': il.invoice_id.number,
                        'product_id': il.product_id.id,
                        'account_id': il.product_id.categ_id.property_account_expense_categ.id,
                        'quantity': il.quantity,
                        'discount': il.discount,
                        'price_unit': cost_price,
                        'sol_start_date': sl.start_date,
                        'sol_end_date': sl.end_date,
                        'sol_confirmation': sl.reservation_number
                    }
                    so_client_order_ref = sl.order_id.client_order_ref
                    so_lead_name = sl.order_id.lead_name

                    data['invoice_line'].append((0, 0, line_vals))

                data['so_client_order_ref'] = so_client_order_ref
                data['so_lead_name'] = so_lead_name
                inv_id = self.create(cr, uid, data, context)
        else:
            self.not_group_by_supplier(cr, uid, invoice, vals, context)
      
    _columns = {
        'so_client_order_ref': fields.char(string="Reference", size=128),
        'so_lead_name': fields.char(string="Client", size=128)
                }
    
    
class account_invoice_line(Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    
    _columns = {
        'sol_start_date': fields.date('Start Date'),
        'sol_end_date': fields.date('End Date'),
        'sol_confirmation': fields.char(string="Confirmation", size=128)
        }      


class account_voucher_line(Model):
    _name = 'account.voucher.line'
    _inherit = 'account.voucher.line'

    _columns = {
        'so_client_order_ref': fields.char(string="Reference", size=128),
        'so_lead_name': fields.char(string="Client", size=128),
        'so_service_name': fields.char(string="Service Name", size=128),
        'sol_confirmation': fields.char(string="Confirmation", size=128)
        }


class account_voucher(Model):
    _name = 'account.voucher'
    _inherit = 'account.voucher'

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        default = super(account_voucher, self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price,
                                                                       currency_id, ttype, date, context=None)
        if default:
            if default['value']['line_dr_ids']:
                line_dr_ids = []
                invoice_pool = self.pool.get('account.invoice')
                invoice_line_pool = self.pool.get('account.invoice.line')
                move_line_pool = self.pool.get('account.move.line')
                line_dr_ids_copy = default['value']['line_dr_ids']
                for line in default['value']['line_dr_ids']:
                    if line['move_line_id']:
                        cr.execute('SELECT i.id ' \
                                   'FROM account_move_line l, account_invoice i ' \
                                   'WHERE l.move_id = i.move_id ' \
                                   'AND l.id = %s',
                                   (line['move_line_id'],))
                        invoice_id = cr.fetchall()[0]
                        invoice_obj = invoice_pool.browse(cr, uid, invoice_id, context=context)
                        move_line_obj = move_line_pool.browse(cr, uid, line['move_line_id'], context=context)
                        invoice_line_ids = invoice_line_pool.search(cr, uid, [('invoice_id', '=', invoice_id)])
                        so_service_name = ''
                        sol_confirmation = ''
                        if invoice_line_ids:
                            for li in invoice_line_pool.browse(cr, uid, invoice_line_ids, context=context):
                                so_service_name += '(' + str(li.name) + ') '
                                sol_confirmation += '(' + str(li.sol_confirmation) + ') '

                        line['so_client_order_ref'] = invoice_obj.so_client_order_ref
                        line['so_lead_name'] = invoice_obj.so_lead_name
                        line['so_service_name'] = so_service_name
                        line['sol_confirmation'] = sol_confirmation
                        line_dr_ids.append(line)

                default['value']['line_dr_ids'] = line_dr_ids or line_dr_ids_copy

        return default


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    