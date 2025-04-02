from dash import Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash import html


def register_callbacks(dash_app, ds_controller, paper_api_service):

    @dash_app.callback(
        [Output('modal-container', 'className'),
         Output('modal-title', 'children'),
         Output('modal-organism', 'children'),
         Output('modal-references', 'children')],
        [Input('plot', 'clickData'),
         Input('close-modal', 'n_clicks')],
        [State('modal-title', 'children')]
    )
    def handle_modal(clickData, close_clicks, current_title):
        ctx = callback_context

        triggered_id = ctx.triggered[0]['prop_id'].split(
            '.')[0] if ctx.triggered else None

        if triggered_id == 'close-modal' and close_clicks:
            return 'modal-hidden', current_title, None, None

        if triggered_id == 'plot' and clickData:
            ds_id = clickData['points'][0]["customdata"][1]
            point_data = ds_controller.get_ds_data_by_id(ds_id)

            modal_title = point_data['title']
            modal_organism = point_data['taxon']

            modal_references = []
            for paper_id in point_data['paper_ids']:
                try:
                    paper_details = paper_api_service.fetch_paper_details(
                        paper_id)
                    modal_references.append(
                        html.A(
                            paper_details['title'],
                            href=f'https://pubmed.ncbi.nlm.nih.gov/{paper_id}',
                            target='_blank'
                        )
                    )
                except Exception as e:
                    print(
                        f"Error fetching paper details for ID {paper_id}: {e}")

            return (
                'modal-visible',
                modal_title,
                modal_organism,
                [
                    html.Div("References:",
                             className='modal-references-heading'),
                    html.Div(modal_references,
                             className='modal-references-items')
                ]
            )

        raise PreventUpdate
