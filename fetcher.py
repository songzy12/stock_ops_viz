import argparse
import pandas as pd
import requests
import os
import time
from io import StringIO

def fetch_and_save_data(ticker, api_key=None, output_dir="data", retries=3, delay=5):
    """
    Fetch historical stock data using Alpha Vantage (CSV format).
    Note: Free tier has limited calls (currently 25 per day).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Fetching data for {ticker} via Alpha Vantage...")
    
    # Use provided key, then check env var, default to 'demo'
    api_key = api_key or os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")
    
    # Using TIME_SERIES_WEEKLY
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={ticker}&apikey={api_key}&datatype=csv"
    
    for attempt in range(retries):
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                content = response.text
                if "Error Message" in content:
                    raise ValueError(f"API Error: {content.strip()}")
                if "Information" in content:
                    print(f"Alpha Vantage Info/Rate Limit: {content.strip()}")
                    time.sleep(delay)
                    continue
                
                df = pd.read_csv(StringIO(content))
                
                if df.empty or "timestamp" not in df.columns:
                    raise ValueError("No valid data received. Check ticker or API limits.")
                
                # Rename columns to match visualizer expectations
                df.rename(columns={'timestamp': 'Date', 'close': 'Close'}, inplace=True)
                
                output_path = os.path.join(output_dir, f"{ticker}_data.csv")
                df.to_csv(output_path, index=False)
                print(f"Data saved successfully to {output_path}")
                return output_path
            
            elif response.status_code == 429:
                print(f"HTTP 429 Rate limited. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            else:
                response.raise_for_status()
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e
    
    raise Exception(f"Failed to fetch data for {ticker} after {retries} attempts.")

def main():
    parser = argparse.ArgumentParser(description="Fetch stock data via Alpha Vantage.")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker symbol")
    parser.add_argument("--apikey", type=str, help="Alpha Vantage API key (overrides ALPHA_VANTAGE_API_KEY env var)")
    parser.add_argument("--outdir", type=str, default="data", help="Output directory")

    args = parser.parse_args()
    
    try:
        fetch_and_save_data(args.ticker, api_key=args.apikey, output_dir=args.outdir)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
