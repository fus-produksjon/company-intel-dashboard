import asyncio
from src.web_scraper import CompanyIntelScraper
from src.dashboard import CompanyDashboard
import os
import json
from dash.dependencies import Input, Output, State
import dash
from dash import html
import dash_bootstrap_components as dbc

class CompanyIntelApp:
    def __init__(self):
        self.scraper = CompanyIntelScraper()
        self.dashboard = CompanyDashboard()
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'logos'), exist_ok=True)
        self.setup_callbacks()

    def setup_callbacks(self):
        """Set up the dashboard callbacks"""
        @self.dashboard.app.callback(
            [Output("company-list", "children"),
             Output("company-header", "children"),
             Output("tab-content", "children"),
             Output("error-message", "children")],
            [Input("add-company-btn", "n_clicks")],
            [State("company-url", "value")]
        )
        def update_dashboard(n_clicks, url):
            if not n_clicks or not url:
                return "", "", "", ""

            try:
                # Create event loop and run scraping
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                company_data = loop.run_until_complete(self.scraper.scrape_company(url))
                loop.close()

                if not company_data.get('name'):
                    return "", "", "", "Could not find company information"

                # Save the data
                self.save_company_data(company_data)

                # Create company card
                company_card = self.create_company_card(company_data)
                
                # Create company details
                company_header = self.create_company_header(company_data)
                
                # Create tab content
                tab_content = self.create_tab_content(company_data)

                return company_card, company_header, tab_content, ""

            except Exception as e:
                return "", "", "", f"Error: {str(e)}"

    def create_company_card(self, company_data):
        """Create a card for the company in the sidebar"""
        return dbc.Card(
            dbc.CardBody([
                html.H5(company_data.get('name', 'Unknown Company'), className="mb-1"),
                html.P(
                    company_data.get('description', '')[:100] + '...' if company_data.get('description') else '',
                    className="small text-muted"
                )
            ]),
            className="mb-3"
        )

    def create_company_header(self, company_data):
        """Create the company header"""
        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.Img(
                        src=company_data.get('logo_url', ''),
                        style={'height': '50px', 'width': 'auto'}
                    ) if company_data.get('logo_url') else None,
                    html.Div([
                        html.H2(company_data.get('name', 'Unknown Company'), className="mb-0"),
                        html.P(company_data.get('description', ''), className="text-muted"),
                    ], className="ms-3")
                ], className="d-flex align-items-center")
            ])
        ])

    def create_tab_content(self, company_data):
        """Create the content for all tabs"""
        return dbc.Card([
            dbc.CardBody([
                html.H3("Company Information"),
                html.Div([
                    html.H5("Stock Information") if company_data.get('stock_info') else None,
                    html.P([
                        html.Strong("Symbol: "), company_data['stock_info']['symbol'], html.Br(),
                        html.Strong("Current Price: "), f"${company_data['stock_info']['current_price']}", html.Br(),
                        html.Strong("Market Cap: "), f"${company_data['stock_info']['market_cap']:,}", html.Br(),
                        html.Strong("Industry: "), company_data['stock_info']['industry']
                    ]) if company_data.get('stock_info') else None,
                ])
            ])
        ])

    def save_company_data(self, company_data):
        """Save company data to JSON file"""
        if not company_data.get('name'):
            return
            
        filename = f"{company_data['name'].lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(company_data, f, indent=4)

    def run(self):
        """Run the dashboard application"""
        port = int(os.environ.get('PORT', 8051))
        self.dashboard.run_server(host='0.0.0.0', port=port, debug=False)

    @property
    def server(self):
        """Get the Flask server for Gunicorn"""
        return self.dashboard.app.server

app = CompanyIntelApp()
server = app.server  # For Gunicorn

if __name__ == "__main__":
    app.run()
