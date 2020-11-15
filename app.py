import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
import dash_html_components as html
import json
from wordcloud import WordCloud
import plotly.graph_objs as go
from io import BytesIO
import base64

app = dash.Dash(
    external_stylesheets=[dbc.themes.COSMO]
)

all_terms = pd.read_csv('db/daily_terms.csv', header=0, names=['term','counts','date'])
freq_terms = pd.read_csv('db/frequent_terms.csv')
freq_bigrams = pd.read_csv('db/frequent_bigrams.csv')
freq_trigrams = pd.read_csv('db/frequent_trigrams.csv')


term_input = dbc.FormGroup(
    [
        dbc.Label("Input term:", html_for="term", className="mr-2"),
        dbc.Input(type="text", id="term", placeholder="text"),
        dbc.Button("Submit", color="primary", id="submit-val", n_clicks=0),
    ],
    className="mr-3",
)

app.layout = dbc.Container([
    html.H1("Trends Analysis for Twitter"),
    html.Hr(),
    html.Div(
        dbc.Form([term_input], inline=True),
        className="m-5"
    ),
    html.Div(id='intermediate-value', style={'display': 'none'}),
    html.Div(id='user-input-value', style={'display': 'none'}),
    html.Div(
        dbc.Row(
            [
                dbc.Col(
                    html.Div(dash_table.DataTable(
                        columns=[{"name": "term", "id": "term", "deletable": True}],
                        editable=True,
                        row_deletable=True,
                        id='userinput-table'
                    )),
                    md=1,
                    className="ml-5"

                ),
                dbc.Col([
                    html.Div(
                        dcc.Graph(id="graph", style={"width": "100%", "display": "inline-block"}),
                    ),
                    html.Div([
                        html.Div(id="wc-id"),
                        html.Div(html.Img(id='image_wc', style={"width": "50%"}),
                        style={'textAlign': 'center'})
                    ])],
                ),
                dbc.Col([
                    html.Div(id="day-stats"),
                    html.Div(dash_table.DataTable(
                        id='day-terms-table',
                        page_size=20,
                        row_selectable="multi",
                        selected_rows=[],
                    ))],
                    md = 2,
                    className = "mr-5"
                 ),
            ],
        ),
    ),
        html.Div(dbc.Alert("Frequent terms", color="primary")),
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
                        md=2,
                        # style={
                        #     "overflowX": "scroll",
                        #     'height': 500},
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
                        md=2,
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
                        md=3,
                    )
                ]
            )],
            className="ml-5"
        )
    ],
    fluid=True,
)


def wordcloud(data):
    wc = WordCloud(background_color='white', width=480, height=360)
    wc.fit_words(data)
    return wc.to_image()

@app.callback([
        Output('day-terms-table', 'data'),
        Output('day-terms-table', 'columns'),
        Output('image_wc', 'src'),
        Output('day-stats', 'children'),
        Output('wc-id', 'children')
    ],
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    print(clickData)
    if clickData:
        point = clickData['points']
        current_frequency = point[0]['y']
        terms_df = all_terms[all_terms['date'] == point[0]['x']][['term','counts']].sort_values(by=['counts'], ascending=False)
        near_frequent_terms = terms_df[terms_df['counts'].between(current_frequency - 2000, current_frequency + 2000)]
        terms_freq = {row['term']:row['counts'] for row in near_frequent_terms[['term','counts']].to_dict('records')}
        img = BytesIO()
        wordcloud(terms_freq).save(img, format='PNG')
        value = dbc.Alert(f'Selected term "{point[0]["hovertext"]}" with frequency = {point[0]["y"]}. '
                          f'Frequent terms for {point[0]["x"]}', color="primary")
        return terms_df[['term','counts']].to_dict('records'),\
               [{"name": i, "id": i} for i in terms_df.columns],\
               'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode()), \
               value,\
               value
    else:
        return [],[],None,None,None


@app.callback(Output('intermediate-value', 'children'),
              [Input('all-terms-table', "derived_virtual_data"),
               Input('all-terms-table', 'derived_virtual_selected_rows'),
               Input('all-bigrams-table', "derived_virtual_data"),
               Input('all-bigrams-table', 'derived_virtual_selected_rows'),
               Input('all-trigrams-table', "derived_virtual_data"),
               Input('all-trigrams-table', 'derived_virtual_selected_rows'),
               Input('day-terms-table', "derived_virtual_data"),
               Input('day-terms-table', 'derived_virtual_selected_rows')])
def save_selection(term_data,
                      term_selected,
                      bigram_data,
                      bigram_selected,
                      trigram_data,
                      trigram_selected,
                      day_data,
                      day_selected):

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
    return selected


@app.callback(Output('userinput-table','data'),
              Input('submit-val', 'n_clicks'),
              [State('term', 'value'),
               State('userinput-table', 'data'),
               State('userinput-table', 'columns')])
def user_input_list(n_clicks, value, rows, columns):
    if n_clicks > 0:
        if rows is not None:
            rows.append({"term": value})
            return rows
        else:
            return [{"term": value}]


@app.callback(Output('graph', 'figure'),
               [Input('userinput-table', 'data'),
               Input('intermediate-value', 'children')])
def update_graph(user_values, selected):
    result = []
    for x in selected:
        result.append(all_terms[all_terms['term'] == x])
    if user_values is not None:
        for y in user_values:
            result.append(all_terms[all_terms['term'] == y['term']])
    if len(result) > 0:
        result = pd.concat(result).to_json(date_format='iso', orient='split')
    try:
        dff = pd.read_json(result, orient='split')
        fig = px.scatter(dff, x="date", y="counts", color="term",
                   hover_name="term")
    except Exception:
        fig = px.scatter()
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)