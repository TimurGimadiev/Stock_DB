# -*- coding: utf-8 -*-
#
#  Copyright 2020 Ramil Nugmanov <nougmanoff@protonmail.com>
#  Copyright 2020 Timur Gimadiev <timur.gimadiev@gmail.com>
#  This file is part of AFIRdb.
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
from base64 import encodebytes
from CGRtools import MoleculeContainer, MRVRead, MRVWrite
from dash import Dash, callback_context
from dash_html_components import Img
from dash.dependencies import Input, Output, State
from io import StringIO, BytesIO
from os import getenv
from layout import get_layout, fields1, fields2
from plugins import external_scripts, external_stylesheets
from CGRdb import Molecule, load_schema
from CGRdbData import MoleculeProperties
from pony.orm import db_session, select
from collections import Counter




MoleculeContainer._render_config['mapping'] = False
color_map = ['rgb(0,104,55)', 'rgb(26,152,80)', 'rgb(102,189,99)', 'rgb(166,217,106)', 'rgb(217,239,139)',
             'rgb(254,224,139)']
db = load_schema('reactions', password='afirdb', port=5432, host='localhost', user='postgres')

def svg2html(svg):
    return 'data:image/svg+xml;base64,' + encodebytes(svg.encode()).decode().replace('\n', '')

def brutto(mol):
    return ''.join(f'{a}{n}' for a, n in
                 sorted(Counter(a.atomic_symbol for _, a in mol.atoms()).items()))

dash = Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
dash.title = 'Stock_DB'
dash.layout = get_layout(dash)
dash.server.secret_key = getenv('SECRET_KEY', 'development')

@dash.callback([Output('table', 'data'), Output('table', 'selected_rows')],
               [Input('editor', 'download'),Input('button', 'n_clicks')],
               [State('radio1', 'value'), State('radio2', 'value'), State('radio3', 'value'),
                State('input1', 'value')])
def search(mrv, button, radio1, radio2, radio3, input1):
    m = None
    ctx = callback_context
    element_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if element_id == 'button' and input1:
        input1 = input1.strip().lower()
        found = []
        if radio2 == 'CAS':
            with db_session:
                if radio1 == 'EMATCH':
                    m = list(select(c for c in MoleculeProperties if str(c.data['CAS No.']).lower() == input1))
                    if m:
                        m = [[x.structure for x in m][0]]
                elif radio1 == 'PMATCH':
                    m = list(select(c for c in MoleculeProperties if input1 in str(c.data['CAS No.']).lower()))
                    if m:
                        m = list(set([x.structure for x in m]))
        elif radio2 == 'NAME':
            with db_session:
                if radio1 == 'EMATCH':
                    m = list(select(c for c in MoleculeProperties if str(c.data['Chemical name']).lower() == input1))
                    if m:
                        m = [[x.structure for x in m][0]]
                elif radio1 == 'PMATCH':
                    m = list(select(c for c in MoleculeProperties if input1 in str(c.data['Chemical name']).lower()))
                    if m:
                        m = list(set([x.structure for x in m]))
        elif radio2 == 'BAR':
            with db_session:
                if radio1 == 'EMATCH':
                    m = list(select(c for c in MoleculeProperties if str(c.data['IASO Barcode No.']).lower() == input1))
                    if m:
                        m = [[x.structure for x in m][0]]
                elif radio1 == 'PMATCH':
                    m = list(select(c for c in MoleculeProperties if input1 in str(c.data['IASO Barcode No.']).lower()))
                    if m:
                        m = list(set([x.structure for x in m]))

    elif element_id == 'editor':
        if mrv:
            with BytesIO(mrv.encode()) as f, MRVRead(f) as i:
                s = next(i)
                s.standardize()
                s.thiele()
            found = []
            with db_session:
                if radio3 == 'SIM':
                    m = Molecule.find_similar(s)
                    if m is not None:
                        m = m.molecules()
                    else:
                        m = None
                elif radio3 == 'EX':
                    m = Molecule.find_structure(s)
                    if m is not None:
                        m = [Molecule.find_structure(s)]
                    else:
                        m = None
                elif radio3 == 'SUB':
                    m = Molecule.find_substructures(s)
                    #print(m)
                    if m is not None:
                        m = m.molecules()
    with db_session:
        if m is None or not m:
            found = [dict([(i['name'], 'No results') for i in fields1])]
        else:
            for h in m:
                entities = list(Molecule[h.id].metadata.data)
                cas = '; '.join(set([x['CAS No.'] for x in entities]))
                names = '; '.join(set([x['Chemical name'] for x in entities]))
                br_formula = brutto(h.structure)
                found.append(dict([(i['name'], j) for i, j in zip(fields1, [br_formula, names, cas])]))
                found[-1]['id'] = h.id
    row = []
    return found, row

@dash.callback([Output('table2', 'data'), Output('editor', 'upload')],
               [Input('table', 'selected_rows'), Input('addrow', 'n_clicks'), Input('confirm', 'submit_n_clicks')],
               [State('table', 'data'), State('editor', 'download'), State('table2', 'columns'),
                State('table2', 'data'), State('editor', 'upload')])
def search(row_id, button, confirm, data, mrv, cols2, rows2, mrv_cur):
        table = [dict([(i["name"], 'No results') for i in fields2])]
        ctx = callback_context
        element_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if row_id and element_id == 'table':
            if 'id' not in data[row_id[0]]:
                return table, mrv
            id = data[row_id[0]]['id']
            with db_session:
                table = []
                for c in Molecule[id].metadata:
                    table.append(c.data)
                    table[-1]['id'] = c.id
                s = Molecule[id].structure
                s.clean2d()
            with StringIO() as f:
                with MRVWrite(f) as o:
                    o.write(s)
                mrv = f.getvalue()

        elif button and element_id == 'addrow':
            rows2.append({c['id']: '' for c in cols2})
            rows2[-1]['id'] = None
            table = rows2
            mrv = mrv_cur

        elif confirm and element_id == 'confirm':
            table = rows2
            mrv = mrv_cur
            #print(rows2)
            if mrv_cur and all((x for x in rows2 for y, x in x.items() if y != 'id')) and len(rows2) > 0:
                if rows2[0]['CAS No.'] == 'No results':
                    rows2.pop(0)
                with BytesIO(mrv.encode()) as f, MRVRead(f) as j:
                    s = next(j)
                    s.standardize()
                    s.thiele()
                    s.clean2d()
                with db_session:
                    m = Molecule.find_structure(s)
                    if not m:
                        m = Molecule(s)
                    to_delete = set([x.id for x in m.metadata]).difference([x['id'] for x in rows2])
                    for i in rows2:
                        if i['id'] is not None:
                            MoleculeProperties[i['id']].data = {j: k for j, k in i.items() if j != 'id'}
                        else:
                            MoleculeProperties(structure=m, data={j: k for j, k in i.items() if j != 'id'})
                    for i in m.metadata:
                        if i.id in to_delete:
                            i.delete()
                with StringIO() as f:
                    with MRVWrite(f) as o:
                        o.write(s)
                    mrv = f.getvalue()
        return table, mrv

@dash.callback(Output('confirm', 'displayed'),[Input('submit', 'n_clicks')])
def display_confirm(value):
    if value:
        return True
    return False



@dash.server.before_request
def db_config():
    db.cgr_db_config()
dash.run_server(port=8008, host="0.0.0.0", debug=False)

__all__ = ['dash']
