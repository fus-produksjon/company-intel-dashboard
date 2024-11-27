# Company Intelligence Dashboard

A web application that scrapes and displays comprehensive company information for marketing executives. The tool automatically collects and visualizes data about companies including revenue, market position, products, operating territories, competitors, and stock market information.

## Features

- Web scraping of company information from public sources
- Stock market data integration using yfinance
- Company logo and brand asset collection
- Interactive dashboard with multiple views:
  - Company Overview
  - Financial Information
  - Market Position
- Data persistence and management
- Modern, responsive UI using Dash and Bootstrap

## Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:8050`

3. Enter a company's URL in the input field and click "Add Company"

## Data Collection

The tool collects the following information:
- Company name and description
- Revenue and financial metrics
- Product portfolio
- Operating territories
- Competitors
- Stock market information (for public companies)
- Company logos and brand assets

## Technical Details

- Built with Python 3.8+
- Uses Selenium for dynamic web scraping
- Dash framework for the dashboard
- Data storage in JSON format
- Asynchronous data collection

## Dependencies

- beautifulsoup4
- requests
- selenium
- pandas
- dash
- yfinance
- python-dotenv
- webdriver-manager
- plotly
- aiohttp
- pillow

## Note

This tool is designed for collecting publicly available information only. Please ensure compliance with websites' terms of service and robots.txt when scraping data.
