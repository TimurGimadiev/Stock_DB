from dash_core_components import Input, RadioItems, ConfirmDialog
from dash_html_components import Div, H1, Hr, H2, Button, Br, Img
from dash_bootstrap_components import Table
from dash_marvinjs import DashMarvinJS
from dash_table import DataTable

readme = '''
# Readme
- Help will be shown here
'''
fields1 = [
        {'name': 'Brutto formula', 'id': 'Brutto formula'},
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
                Div([
                    Table(id='table', columns=fields1,
                              fixed_rows={'headers': True, 'data': 0},
                              row_selectable='single',
                              style_data={
                                  'whiteSpace': 'normal',
                                  'height': 'auto'},
                              style_table={ 'overflowY': 'hidden', 'overflowX': 'hidden',
                                           'margin-left': '0px'},
                              style_cell={'textAlign': 'left', 'padding': '20px', 'padding-left': '20px',
                                          'height': 'auto','width':'auto', 'whiteSpace': 'normal'},
                              style_as_list_view=True,
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
                  row_1, Hr(), row_2, Hr(), row_3, Hr(), row_4])
    return layout
