import aiohttp
import asyncio
from bs4 import BeautifulSoup
import yfinance as yf
import os
import re
from urllib.parse import urljoin, urlparse
import logging
from PIL import Image
from io import BytesIO
import json
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyIntelScraper:
    def __init__(self):
        self.session = None
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.logos_dir = os.path.join(self.data_dir, 'logos')
        os.makedirs(self.logos_dir, exist_ok=True)

    async def create_session(self):
        """Create aiohttp session if not exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        return self.session

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def scrape_company(self, url):
        """Main method to scrape company information"""
        try:
            session = await self.create_session()
            
            # Initialize company data
            company_data = {
                'url': url,
                'name': None,
                'description': None,
                'logo_url': None,
                'stock_info': None
            }
            
            # Get basic company info
            try:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Try to get company name
                        company_data['name'] = self.extract_company_name(soup, url)
                        
                        # Try to get company description
                        company_data['description'] = self.extract_description(soup)
                        
                        # Try to get logo URL
                        company_data['logo_url'] = await self.find_logo(soup, url)
                        
                        # Try to get stock information
                        if company_data['name']:
                            company_data['stock_info'] = await self.get_stock_info(company_data['name'])
            except Exception as e:
                logger.error(f"Error accessing URL {url}: {str(e)}")
                company_data['error'] = f"Could not access website: {str(e)}"
                
            return company_data
            
        except Exception as e:
            logger.error(f"Error scraping company {url}: {str(e)}")
            return {'error': str(e)}
        
        finally:
            await self.close_session()

    def extract_company_name(self, soup, url):
        """Extract company name from various sources"""
        try:
            # Try meta tags first
            meta_title = soup.find('meta', property='og:site_name')
            if meta_title and meta_title.get('content'):
                return meta_title['content']
                
            # Try title tag
            title = soup.find('title')
            if title:
                # Clean up common suffixes
                name = title.text.split('|')[0].split('-')[0].strip()
                name = re.sub(r'\s*(Official Site|Home|Website).*$', '', name, flags=re.IGNORECASE)
                return name
                
            # Try domain name
            domain = urlparse(url).netloc
            name = domain.split('.')[-2].capitalize()
            return name
            
        except Exception as e:
            logger.error(f"Error extracting company name: {str(e)}")
            return None

    def extract_description(self, soup):
        """Extract company description from meta tags"""
        try:
            # Try different meta tags
            for meta in soup.find_all('meta'):
                if meta.get('name') in ['description', 'og:description']:
                    content = meta.get('content')
                    if content:
                        return content
                
            # Try to find first paragraph
            first_p = soup.find('p')
            if first_p:
                return first_p.text.strip()
                
            return None
            
        except Exception as e:
            logger.error(f"Error extracting description: {str(e)}")
            return None

    async def find_logo(self, soup, url):
        """Find company logo URL"""
        try:
            # Try common logo locations
            logo_selectors = [
                {'tag': 'link', 'rel': 'icon'},
                {'tag': 'link', 'rel': 'shortcut icon'},
                {'tag': 'meta', 'property': 'og:image'},
                {'tag': 'img', 'class_': re.compile(r'logo|brand', re.I)},
            ]
            
            for selector in logo_selectors:
                element = soup.find(**selector)
                if element:
                    logo_url = element.get('href') or element.get('content') or element.get('src')
                    if logo_url:
                        return urljoin(url, logo_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding logo: {str(e)}")
            return None

    async def get_stock_info(self, company_name):
        """Get stock information using multiple approaches"""
        try:
            # Remove common company suffixes
            search_name = re.sub(r'\s+(Inc\.?|Corp\.?|Ltd\.?|LLC|Limited)$', '', company_name, flags=re.I)
            
            # Try direct symbol lookup
            symbol = yf.Ticker(search_name)
            info = symbol.info
            
            if info and 'regularMarketPrice' in info:
                return {
                    'symbol': symbol.ticker,
                    'current_price': info.get('regularMarketPrice'),
                    'market_cap': info.get('marketCap'),
                    'industry': info.get('industry', 'Unknown')
                }
            
            # Try search
            search_results = await self.search_stock_symbol(search_name)
            if search_results:
                symbol = yf.Ticker(search_results)
                info = symbol.info
                if info and 'regularMarketPrice' in info:
                    return {
                        'symbol': symbol.ticker,
                        'current_price': info.get('regularMarketPrice'),
                        'market_cap': info.get('marketCap'),
                        'industry': info.get('industry', 'Unknown')
                    }
                    
        except Exception as e:
            logger.warning(f"Could not get stock info for {company_name}: {str(e)}")
            
        return None

    async def search_stock_symbol(self, company_name):
        """Search for stock symbol using various methods"""
        try:
            # This is a simplified version. In practice, you might want to use
            # a proper stock symbol lookup API or database
            common_exchanges = ['', '.OL', '.ST', '.CO', '.HE', '.DE']
            
            for exchange in common_exchanges:
                try:
                    symbol = f"{company_name}{exchange}"
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    if info and 'regularMarketPrice' in info:
                        return symbol
                except:
                    continue
                    
            return None
            
        except Exception as e:
            logger.error(f"Error searching stock symbol: {str(e)}")
            return None

    def save_logo(self, logo_url, company_name):
        """Save company logo to disk"""
        if not logo_url or not company_name:
            return None
            
        try:
            response = requests.get(logo_url, verify=False)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                
                # Convert to PNG if necessary
                if img.format != 'PNG':
                    img = img.convert('RGBA')
                
                filename = f"{company_name.lower().replace(' ', '_')}_logo.png"
                filepath = os.path.join(self.logos_dir, filename)
                
                img.save(filepath, 'PNG')
                return filepath
                
        except Exception as e:
            logger.error(f"Error saving logo for {company_name}: {str(e)}")
            return None
