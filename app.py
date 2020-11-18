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


def build_freq_table(id, data, value):
    return html.Div([
        html.H3([dbc.Badge(value, className="ml-1")]),
        dash_table.DataTable(
                            id=id,
                            columns=[{"name": i, "id": i} for i in data.columns],
                            page_size=30,
                            row_selectable="multi",
                            selected_columns=[],
                            selected_rows=[],
                            data=data.to_dict('records'),
                        )],
            className="m-5"
            )

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
                    md=2,
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
        html.Hr(),
        html.Div([
            dbc.Row(
                [
                    dbc.Col(
                        build_freq_table("all-terms-table", freq_terms, "Terms"),
                        md=4,
                    ),
                    dbc.Col(
                        build_freq_table("all-bigrams-table", freq_bigrams, "Bigrams"),
                        md=4,
                    ),
                    dbc.Col(
                        build_freq_table("all-trigrams-table", freq_trigrams, "Trigrams"),
                        md=4,
                    )
                ]
            )],
            className="ml-5"
        )
    ],
    fluid=True,
)


def wordcloud(data):
    wc = WordCloud(background_color='white', width=460, height=320)
    wc.fit_words(data)
    return wc.to_image()

@app.callback([
        Output('day-terms-table', 'data'),
        Output('day-terms-table', 'columns'),
        Output('day-terms-table', 'selected_rows'),
        Output('image_wc', 'src'),
        Output('day-stats', 'children'),
        Output('wc-id', 'children')
    ],
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData:
        point = clickData['points']
        current_frequency = point[0]['y']
        terms_df = all_terms[all_terms['date'] == point[0]['x']][['term','counts']].sort_values(by=['counts'], ascending=False)
        max_frequency = terms_df['counts'].max()
        current_frequency_percent = (current_frequency*100) / max_frequency
        top_freq = current_frequency_percent+current_frequency_percent*0.2
        bottom_freq = current_frequency_percent-current_frequency_percent*0.2
        top_freq_value = round((max_frequency*top_freq)/100)
        bottom_freq_value = round((max_frequency*bottom_freq)/100)
        near_frequent_terms = terms_df[terms_df['counts'].between(bottom_freq_value, top_freq_value)]
        terms_freq = {row['term']:row['counts'] for row in near_frequent_terms[['term','counts']].to_dict('records')}
        img = BytesIO()
        wordcloud(terms_freq).save(img, format='PNG')
        value = html.H3([point[0]["hovertext"], dbc.Badge(f'frequency: {point[0]["y"]}', className="ml-1"), dbc.Badge(f'date: {point[0]["x"]}', className="ml-1")])
        value_1 = html.H3([point[0]["hovertext"], dbc.Badge(f'frequencies between {bottom_freq_value} and {top_freq_value}', className="ml-2")])
        return terms_df[['term','counts']].to_dict('records'),\
               [{"name": i, "id": i} for i in terms_df.columns],\
                [],\
               'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode()), \
               value,\
               value_1
    else:
        return [],[],[],None,None,None


@app.callback(Output('userinput-table', 'data'),
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


@app.callback(Output('intermediate-value', 'children'),
              [Input('all-terms-table', "derived_virtual_data"),
               Input('all-terms-table', 'derived_virtual_selected_rows'),
               Input('all-bigrams-table', "derived_virtual_data"),
               Input('all-bigrams-table', 'derived_virtual_selected_rows'),
               Input('all-trigrams-table', "derived_virtual_data"),
               Input('all-trigrams-table', 'derived_virtual_selected_rows'),
               Input('day-terms-table', "derived_virtual_data"),
               Input('day-terms-table', 'derived_virtual_selected_rows')]
              )
def user_input_list(term_data,
                    term_selected,
                    bigram_data,
                    bigram_selected,
                    trigram_data,
                    trigram_selected,
                    day_data,
                    day_selected,
                    ):
    selected = []
    if term_data is not None:
        [row['term'] for i, row in enumerate(term_data) if i in term_selected if term_data is not None]
        for i, row in enumerate(term_data):
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


@app.callback(Output('graph', 'figure'),
            [Input('intermediate-value', 'children'),
             Input('userinput-table', 'data')],
             [State('userinput-table', 'data'),
             State('graph', 'figure')])
def update_graph(intermediate, userinput, data, previous_figure):
    try:
        dff = pd.read_json(intermediate, orient='split')
        try:
            fig = px.scatter(pd.concat([display_userinput(userinput),dff]), x="date", y="counts", color="term", hover_name="term")
        except Exception:
            fig = px.scatter(dff, x="date", y="counts", color="term", hover_name="term")
    except Exception:
        try:
            fig = px.scatter(display_userinput(userinput), x="date", y="counts", color="term",
                             hover_name="term")
        except Exception:
            fig = px.scatter()
    return fig



def display_userinput(userinput):
    result = []
    for x in userinput:
        result.append(all_terms[all_terms['term'] == x['term']])
    if len(result) > 0:
        result = pd.concat(result).to_json(date_format='iso', orient='split')
    return pd.read_json(result, orient='split')


if __name__ == '__main__':
    app.run_server(debug=True)