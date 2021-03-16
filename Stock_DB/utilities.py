# -*- coding: utf-8 -*-
#
#  Copyright 2020 Timur Gimadiev <timur.gimadiev@gmail.com>
#  Copyright 2020 Pavel Sidorov <pavel.o.sidorov@gmail.com>
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
from base64 import b64decode
from CGRtools import smiles
from CGRdb import Molecule
from CGRdbData import MoleculeProperties
from dash_html_components import Div
from io import StringIO, BytesIO
import pandas as pd
from pony.orm import db_session, select, PrimaryKey, Required


req_fields = {"Chemical name", "Maker name", "CAS No.", "Quantity", "Quantity unit", "IASO Barcode No.",
                  "Storage location (JP) hierarchy4", "Storage location (JP) hierarchy5", "Entry date", "Old"}
valid_keys = ["Chemical name", "Maker", "CAS No.", "Quantity", "Quantity unit", "IASO Barcode No.",
                  "Storage location (JP) hierarchy4", "Storage location (JP) hierarchy5", "Entry date", "Old"]

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = b64decode(content_string)
    try:
        if '.xls' in filename:
            # Assume that the user uploaded an excel file
            return input_from_excel(BytesIO(decoded))
    except Exception as e:
        print(e)
        return Div([
            'There was an error processing this file.'
        ])


def upload_properties(structure, properties):


    for k in properties.keys():
        if k not in valid_keys:
            print("Property", k, "is not valid for DB")
            return
    with db_session:
        found = Molecule.find_structure(structure)
        if not found:
            print(structure)
            print("Molecule not found in DB")
            print("Adding to DB...")
            m = Molecule(structure)
            p = MoleculeProperties(structure=m, data=properties)
        else:
            print("Molecule is found in DB:", structure)
            entries = list(found.metadata.data)
            for e in entries:
                is_copy = True
                for k in valid_keys:
                    if e[k] != properties[k]:
                        is_copy = False
                        break
                if is_copy:
                    print("Entry is already in DB")
                    return
            else:
                print("Adding properties entry")
                p = MoleculeProperties(structure=found.id, data=properties)


def input_from_excel(excel_file):
    print("here")
    chemicals = pd.read_excel(excel_file)

    if len(set(chemicals.columns.values.tolist()).intersection(req_fields)) == 10:
        pass
    else:
        return Div(['''Please check if your Excel file has all 10 required fields: Chemical name,
                    Maker name, CAS No., Quantity, Quantity unit, IASO Barcode No.,
                    Storage location (JP) hierarchy4, Storage location (JP) hierarchy5, Entry date, Old'''])

    entries_good = []
    entries_bad = []
    with db_session:
        for i in Molecule.select():
            i.delete()
        print(len(Molecule.select()))
    for i, row in chemicals.iterrows():
        c = row["SMILES"]
        try:
            a = smiles(c)
            print(a)
            a.standardize()
            a.thiele()
            a.clean2d()
            entries_good.append({"structure": a,
                                 "Chemical name": row["Chemical name"].rstrip(" "),
                                 "Maker": row["Maker name"].rstrip(" "),
                                 "CAS No.": row["CAS No."].rstrip(" "),
                                 "Quantity": row["Quantity"],
                                 "Quantity unit": row["Quantity unit"].rstrip(" "),
                                 "IASO Barcode No.": row["IASO Barcode No."].rstrip(" "),
                                 "Storage location (JP) hierarchy4": row["Storage location (JP) hierarchy4"].rstrip(" "),
                                 "Storage location (JP) hierarchy5": row["Storage location (JP) hierarchy5"].rstrip(" "),
                                 "Entry date": row["Entry date"].rstrip(" "),
                                 "Old": row["Old"].rstrip(" ")})
        except:
            print("Some error in:", i, ",", c)
            entries_bad.append((i, c))
    print("Table is read, found", len(entries_bad), "bad entries,", len(entries_good), "good entries")
    for e in entries_good:
        upload_properties(structure=e["structure"], properties={x: e[x] for x in e if x not in ["structure"]})
    print("Uploaded to DB")
    return Div([
            '''There was {} entities, {} of them were not processed due to errors. 
            Folowing row(s) have problems: {}'''.format(len(entries_good), len(entries_bad), [x+2 for x, _ in entries_bad])],
            style={"maxHeight": "400px", "overflow": "scroll"})


def write_excel():
    res = pd.DataFrame(columns=req_fields)
    with db_session:
        for m in Molecule.select():
            for e in list(m.metadata.data):
                e.update({"SMILES": str(m.structure)})
                tmp = pd.DataFrame.from_dict(e)
                res = pd.concat([res, tmp], ignore_index=True)
    output = BytesIO()
    # Use the StringIO object as the filehandle.
    writer = pd.ExcelWriter("tmp", engine='xlsxwriter')
    writer.book.filename = output
    res.to_excel(writer)
    writer.save()
    output.seek(0)
    #xlsx_data = output.getvalue()
    return output#xlsx_data



