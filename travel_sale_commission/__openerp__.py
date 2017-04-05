# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
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

{
    "name": "Travel Agency - Sale Commission",
    "version": "0.1",
    "author": "OpenJAF.",
    "website": "http://www.openjaf.com",
    "category": "Sales",
    "description": """

Base module for sale commission of OCA
========================================================================

    """,
    "depends": ['base',
                'account',
                'product',
                'sale',
                'travel_core'],
    "init_xml": [],
    "data": [
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "views/sale_commission_view.xml",
        "views/sale_vat_view.xml",
        "views/sale_order_view.xml",
        "views/account_invoice_view.xml",
        'report/reports.xml',
        'data/data.xml',
        'static/src/xml/base_static.xml'
    ],
    "demo_xml": [],
    "application": False,
    "installable": True,
}
