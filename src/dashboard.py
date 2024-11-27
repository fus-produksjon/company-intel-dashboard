import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import json
import os

class CompanyDashboard:
    def __init__(self):
        external_stylesheets = [
            dbc.themes.BOOTSTRAP,
            dbc.icons.FONT_AWESOME
        ]
        self.app = dash.Dash(
            __name__,
            external_stylesheets=external_stylesheets,
            suppress_callback_exceptions=True,
            title="Company Intelligence Dashboard"
        )
        self.setup_layout()
        
    def setup_layout(self):
        """Create the dashboard layout"""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Company Intelligence Dashboard", 
                           className="text-primary text-center mb-4"),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.InputGroup([
                                dbc.Input(
                                    id="company-url",
                                    placeholder="Enter company URL (e.g., https://www.company.com)...",
                                    type="url",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Add Company",
                                    id="add-company-btn",
                                    color="primary",
                                    className="ms-2"
                                ),
                            ]),
                            html.Div(
                                id="error-message",
                                className="text-danger mt-2"
                            )
                        ])
                    ], className="mb-4")
                ])
            ]),
            
            dbc.Row([
                # Sidebar with company list
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Tracked Companies"),
                        dbc.CardBody(
                            html.Div(id="company-list")
                        )
                    ])
                ], width=3),
                
                # Main content area
                dbc.Col([
                    html.Div(id="company-header", className="mb-4"),
                    dbc.Card([
                        dbc.CardHeader(
                            dbc.Tabs([
                                dbc.Tab(label="Overview", tab_id="tab-overview"),
                                dbc.Tab(label="Financial", tab_id="tab-financial"),
                                dbc.Tab(label="Market", tab_id="tab-market"),
                            ], id="company-tabs", active_tab="tab-overview")
                        ),
                        dbc.CardBody(
                            html.Div(id="tab-content")
                        )
                    ])
                ], width=9)
            ])
        ], fluid=True, className="p-4")

    def run_server(self, debug=True, port=8050, host="127.0.0.1"):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port, host=host)
