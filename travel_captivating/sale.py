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