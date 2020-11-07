import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
import json
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)


terms = pd.read_csv('db/all_terms.csv', header=0, names=['term','counts','date'])
bigrams = pd.read_csv('db/all_bigrams.csv', header=0, names=['term','counts','date'])
trigrams = pd.read_csv('db/all_trigrams.csv', header=0, names=['term','counts','date'])
freq_terms = pd.read_csv('db/frequent_terms.csv')
freq_bigrams = pd.read_csv('db/frequent_bigrams.csv')
freq_trigrams = pd.read_csv('db/frequent_trigrams.csv')


term_input = dbc.FormGroup(
    [
        dbc.Label("Input term:", html_for="term", className="mr-2"),
        dbc.Input(type="text", id="term", placeholder="text"),
        dbc.Button("Submit", color="primary", id="submit-val"),
    ],
    className="mr-3",
)


# check_list = dcc.Checklist(
#     id="selected-terms",
#     options=[
#         {'label': 'New York City', 'value': 'NYC'},
#         {'label': 'Montréal', 'value': 'MTL'},
#         {'label': 'San Francisco', 'value': 'SF'}
#     ],
#     value=['NYC', 'MTL']
# )

app.layout = dbc.Container([
    dcc.Store(id="store"),
    html.H1("Trends Analysis for Twitter"),
    html.Hr(),
    html.Div([
        dbc.Form([term_input],
                 inline=True),
        html.Div(id='intermediate-value', style={'display': 'none'}),
        # html.Br(),
        # html.Div([check_list]),
        dcc.Graph(id="graph", style={"width": "75%", "display": "inline-block"}),
        html.Div([dbc.Alert("Frequent terms for current date", color="primary")]),
        html.Div([
             dbc.Row(
                 [
                     dbc.Col(
                         html.Div([dash_table.DataTable(
                             id='day-terms-table',
                             page_size=20,
                         )]),
                         width={"size": 4},
                         style={
                             "overflowX": "scroll",
                             'height': 300},
                     ),
                     dbc.Col(
                         html.Div([dash_table.DataTable(
                             id='day-bigram-table',
                             page_size=20,
                         )]),
                         width={"size": 4},
                         style={
                             "overflowX": "scroll",
                             'height': 300},
                     ),
                     dbc.Col(
                         html.Div([dash_table.DataTable(
                             id='day-trigram-table',
                             page_size=20,
                         )]),
                         width={"size": 4},
                         style={
                             "overflowX": "scroll",
                             'height': 300},
                     )
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
        Output('day-bigram-table', 'data'),
        Output('day-bigram-table', 'columns'),
        Output('day-trigram-table', 'data'),
        Output('day-trigram-table', 'columns')
    ],
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData:
        point = clickData['points']
        terms_df = terms[terms['date'] == point[0]['x']][['term','counts']].sort_values(by=['counts'], ascending=False)
        bigrams_df = bigrams[bigrams['date'] == point[0]['x']][['term','counts']].sort_values(by=['counts'], ascending=False)
        trigrams_df = trigrams[trigrams['date'] == point[0]['x']][['term','counts']].sort_values(by=['counts'], ascending=False)
        return terms_df[['term','counts']].to_dict('records'),\
               [{"name": i, "id": i} for i in terms_df.columns],\
               bigrams_df[['term','counts']].to_dict('records'),\
               [{"name": i, "id": i} for i in bigrams_df.columns],\
               trigrams_df[['term','counts']].to_dict('records'), \
               [{"name": i, "id": i} for i in trigrams_df.columns]
    else:
        return [],[],[],[],[],[]


@app.callback(Output('intermediate-value', 'children'),
              [Input('all-terms-table', "derived_virtual_data"),
               Input('all-terms-table', 'derived_virtual_selected_rows'),
               Input('submit-val', 'n_clicks'),
               State('term', 'value')])
def update_graph_data(derived_virtual_data, derived_virtual_selected_rows, n_clicks, value):
    if not derived_virtual_selected_rows:
        selected = [value] if value is not None else ['']
    else:
        selected = [value] if value is not None else []
    if derived_virtual_data is not None:
        for i,row in enumerate(derived_virtual_data):
            if i in derived_virtual_selected_rows:
                selected.append(row['term'])
        result = []
        for x in selected:
            if len(x.split()) == 1:
                result.append(terms[terms['term'] == x])
            elif len(x.split()) == 2:
                result.append(bigrams[bigrams['term'] == x])
            elif len(x.split()) == 3:
                result.append(trigrams[trigrams['term'] == x])
        if len(result) > 0:
            result = pd.concat(result).to_json(date_format='iso', orient='split')
            return result
        else:
            return ''
    else:
        return ''


if __name__ == '__main__':
    app.run_server(debug=True)