# -*- coding: utf-8 -*-
#
#  Copyright 2020 Timur Gimadiev <timur.gimadiev@gmail.com>
#  This file is part of Warehouse DB.
#
#  AFIRdb is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from dash_core_components import Input, RadioItems, ConfirmDialog, Upload, Loading
from dash_html_components import Div, H1, Hr, H2, H4, Button, Br, A
#from dash_bootstrap_components import Table
from dash_marvinjs import DashMarvinJS
from dash_table import DataTable
from pony.orm import db_session, select, PrimaryKey, Required
from CGRdb import load_schema, LazyEntityMeta
from TimeStamp import ModificationStamp
import time

readme = '''
# Readme
- Help will be shown here
'''
fields1 = [
        {'name': 'Structure', 'id': 'Structure', 'presentation': 'markdown'},
        {'name': 'Empirical formula', 'id': 'Brutto formula'},
        {'name': 'Chemical name', 'id': 'Chemical name'},
        {'name': 'CAS No.', 'id': 'CAS No.'}]


fields2 = [
        {'name': 'CAS No.', 'id': 'CAS No.'},
        {'name': 'Chemical name', 'id': 'Chemical name'},
        {'name': 'Maker', 'id': 'Maker'},
        {'name': 'Quantity', 'id': 'Quantity'},
        {'name': 'Quantity unit', 'id': 'Quantity unit'},
        {'name': 'IASO Barcode No.', 'id': 'IASO Barcode No.'},
        {'name': 'Storage location (JP) hierarchy4', 'id': 'Storage location (JP) hierarchy4'},
        {'name': 'Storage location (JP) hierarchy5', 'id': 'Storage location (JP) hierarchy5'},
        {'name': 'Entry date', 'id': 'Entry date'},
        {'name': 'Old', 'id': 'Old'}]

def get_layout(app):
    with db_session:
        res = select((x.id, x.FileName, x.Time) for x in ModificationStamp).order_by(-1).first()
        name = res[1]
        date = res[2]
    row_0 = Div([H2("Upload to Database (excel file)", style={'textAlign': 'left'}),
    Upload(
        id='upload-data',
        children=Div([
            'Drag and Drop or ',
            A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
        Loading(
            id="loading",
            children=[Div(id='output-data-upload')],
            type="default",
        ),
    ])

    row_1 = Div([
                Div([
                    H2("Text input", style={'textAlign': 'left'}),
                    RadioItems(id='radio1',
                               options=[
                                   {'label': 'Partial match', 'value': 'PMATCH'},
                                   {'label': 'Exact match', 'value': 'EMATCH'}
                               ],
                               value='EMATCH',
                               labelStyle={'display': 'inline-block', }
                               ),
                    Input(id="input1", type="text", placeholder="Query"),
                    Br(),
                    Button('Start text search', id='button')
                ], className='col-6'),
                Div([
                    H2("Search field", style={'textAlign': 'left'}),
                    RadioItems(id='radio2',
                               options=[
                                   {'label': 'Chemical name', 'value': 'NAME'},
                                   {'label': 'CAS Number', 'value': 'CAS'},
                                   {'label': 'IASO Barcode No.', 'value': 'BAR'}
                               ],
                               value='NAME',
                               labelStyle={'display': 'inline-block', }
                               ),
                ], className='col-6')
            ], className='row')
    row_2 = Div([
                Div([H2("Graphical search type", style={'textAlign': 'left'}),
                     RadioItems(id='radio3',
                         options=[
                             {'label': 'Similarity ', 'value': 'SIM'},
                             {'label': 'Substructural ', 'value': 'SUB'},
                             {'label': 'Exact ', 'value': 'EX'}
                         ],
                         value='SIM',
                         labelStyle={'display': 'inline-block',}
                     ),
                    DashMarvinJS(id='editor', marvin_url=app.get_asset_url('mjs/editor.html'), marvin_width='100%')
            ], className='col-6'),
                Div([H2("Search results", style={'textAlign': 'left'}),
                    DataTable(id='table', columns=fields1,
                              fixed_rows={'headers': True, 'data': 0},
                              row_selectable='single',
                              style_data={
                                  'whiteSpace': 'normal',
                                  'height': 'auto','width':'auto' },
                              style_table={ 'overflowY': 'hidden', 'overflowX': 'hidden',
                                           'margin-left': '0px'},
                              style_cell={'textAlign': 'left', 'padding': '5px', 'height': 'auto',
                                          'padding-left': '17px',
                                          'whiteSpace': 'normal',
                                          'minWidth': '10px', 'maxWidth': '150px'},
                              style_as_list_view=True,
                              style_cell_conditional=[
                                {'if': {'column_id': 'Picture'},
                                   'width': '60%'},
                                {'if': {'column_id': 'Brutto formula'},
                                   'width': '10%'},
                                {'if': {'column_id': 'Chemical name'},
                                   'width': '15%'},
                                {'if': {'column_id': 'CAS No.'},
                                   'width': '10%'},
                               ],
                              )
                ], className='col-6')
            ], className='row')
    row_3 = DataTable(id='table2', columns=fields2,
                       fixed_rows={'headers': True, 'data': 0},
                       #row_selectable='single',
                       editable=True,
                      row_deletable=True,
                       style_data={
                           'whiteSpace': 'normal',
                           'height': 'auto'},
                       style_table={'maxHeight': '500px', 'overflowY': 'hidden', 'overflowX': 'hidden', 'margin-left': '0px'},
                       style_cell={'textAlign': 'left', 'padding': '10px', 'padding-left': '20px', 'height': 'auto',
                                   'whiteSpace': 'normal', 'minWidth': '120px', 'width': '150px'},
                      #style_cell_conditional=[
                      #    {'if': {'column_id': 'Quantity'},
                      #     'width': '150px'},
                      #   {'if': {'column_id': 'Quantity unit'},
                      #     'width': '150px'},
                      #],
                       style_as_list_view=True)
    row_4 = Div([Button('Add Row', id='addrow', n_clicks=0),
                 Button('Submit changes', id='submit', n_clicks=0),
                 ConfirmDialog(
                     id='confirm',
                     message='All changes will be applied from now! Are you sure you want to continue?',
                 )
                 ])



    layout = Div([H1("Chemicals Storage", style={'textAlign': 'center'}),
                  H4("Last update with file {} uploaded at {}".format(name, time.ctime(int(date)) if date != 'never' else date), id="update", style={'textAlign': 'center'}), row_0, Hr(),
                  row_1, Hr(), row_2, Hr(), row_3, Hr(), row_4])
    return layout
