import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
import json

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


all_terms = pd.read_csv('db/daily_terms.csv', header=0, names=['term','counts','date'])
freq_terms = pd.read_csv('db/frequent_terms.csv')
freq_bigrams = pd.read_csv('db/frequent_bigrams.csv')
freq_trigrams = pd.read_csv('db/frequent_trigrams.csv')

selected_items = []

term_input = dbc.FormGroup(
    [
        dbc.Label("Input term:", html_for="term", className="mr-2"),
        dbc.Input(type="text", id="term", placeholder="text"),
        dbc.Button("Submit", color="primary", id="submit-val"),
    ],
    className="mr-3",
)

app.layout = dbc.Container([
    dcc.Store(id="store"),
    html.H1("Trends Analysis for Twitter"),
    html.Hr(),
    html.Div([
        dbc.Form([term_input],
                 inline=True),
        html.Div(id='intermediate-value', style={'display': 'none'}),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
        html.Div([dbc.Alert("Frequent terms for current date", color="primary")]),
        html.Div([
             dbc.Row(
                 [
                     dbc.Col(
                         html.Div([dash_table.DataTable(
                             id='day-terms-table',
                             page_size=20,
                             row_selectable="multi",
                             selected_columns=[],
                             selected_rows=[],
                         )]),
                         width={"size": 4},
                         style={
                             "overflowX": "scroll",
                             'height': 300},
                     ),
                 ])
                ],
            ),
        html.Div([dbc.Alert("Frequent terms", color="primary")]),
        html.Div([
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([dash_table.DataTable(
                            id='all-terms-table',
                            columns=[{"name": i, "id": i} for i in freq_terms.columns],
                            page_size=30,
                            row_selectable="multi",
                            selected_columns=[],
                            selected_rows=[],
                            data=freq_terms.to_dict('records'),
                        )]),
                        width={"size": 4},
                        style={
                            "overflowX": "scroll",
                            'height': 500},
                    ),
                    dbc.Col(
                        html.Div([dash_table.DataTable(
                            id='all-bigrams-table',
                            columns=[{"name": i, "id": i} for i in freq_bigrams.columns],
                            page_size=30,
                            row_selectable="multi",
                            selected_columns=[],
                            selected_rows=[],
                            data=freq_bigrams.to_dict('records'),
                        )]),
                        width={"size": 4},
                        style={
                            "overflowX": "scroll",
                            'height': 500},
                    ),
                    dbc.Col(
                        html.Div([dash_table.DataTable(
                            id='all-trigrams-table',
                            columns=[{"name": i, "id": i} for i in freq_trigrams.columns],
                            page_size=30,
                            row_selectable="multi",
                            selected_columns=[],
                            selected_rows=[],
                            data=freq_trigrams.to_dict('records'),
                        )]),
                        width={"size": 4},
                        style={
                            "overflowX": "scroll",
                            'height': 500},
                    ),
                ]
            ),
        ])
    ])
    ]
)


@app.callback(Output('graph', 'figure'),
              [Input('intermediate-value', 'children')])
def update_graph(jsonified_cleaned_data):
    try:
        dff = pd.read_json(jsonified_cleaned_data, orient='split')
        fig = px.scatter(dff, x="date", y="counts", color="term",
                   hover_name="term", height=700, width=1200)
    except Exception:
        fig = px.scatter()
    return fig


@app.callback([
        Output('day-terms-table', 'data'),
        Output('day-terms-table', 'columns'),
    ],
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData:
        point = clickData['points']
        terms_df = all_terms[all_terms['date'] == point[0]['x']][['term','counts']].sort_values(by=['counts'], ascending=False)
        return terms_df[['term','counts']].to_dict('records'),\
               [{"name": i, "id": i} for i in terms_df.columns]
    else:
        return [],[]



@app.callback(Output('intermediate-value', 'children'),
              [Input('all-terms-table', "derived_virtual_data"),
               Input('all-terms-table', 'derived_virtual_selected_rows'),
               Input('all-bigrams-table', "derived_virtual_data"),
               Input('all-bigrams-table', 'derived_virtual_selected_rows'),
               Input('all-trigrams-table', "derived_virtual_data"),
               Input('all-trigrams-table', 'derived_virtual_selected_rows'),
               Input('day-terms-table', "derived_virtual_data"),
               Input('day-terms-table', 'derived_virtual_selected_rows'),
               Input('submit-val', 'n_clicks'),
               State('term', 'value')])
def update_graph_data(term_data,
                      term_selected,
                      bigram_data,
                      bigram_selected,
                      trigram_data,
                      trigram_selected,
                      day_data,
                      day_selected,
                      n_clicks, value):
    if value is not None:
        selected = [value]
    else:
        selected = []
    if term_data is not None:
        for i,row in enumerate(term_data):
            if i in term_selected:
                selected.append(row['term'])
    if bigram_data is not None:
        for i, row in enumerate(bigram_data):
            if i in bigram_selected:
                selected.append(row['bigram'])
    if trigram_data is not None:
        for i, row in enumerate(trigram_data):
            if i in trigram_selected:
                selected.append(row['trigram'])
    if day_data is not None:
        for i, row in enumerate(day_data):
            if i in day_selected:
                selected.append(row['term'])
    result = []
    for x in selected:
        result.append(all_terms[all_terms['term'] == x])
    if len(result) > 0:
        result = pd.concat(result).to_json(date_format='iso', orient='split')
        return result
    else:
        return ''


if __name__ == '__main__':
    app.run_server(debug=True)