import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_from_csv(csv_path, op_dates=None, start_date="2022-07-22", output_dir="output"):
    """Load stock data from CSV and visualize with optional operation dates."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input file not found: {csv_path}")
        
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Ensure Date is datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Adjust pre-split prices (2022-07-22 20-for-1 stock split)
    split_date = pd.to_datetime("2022-07-22")
    df.loc[df.index < split_date, 'Close'] /= 20

    # Filter data by start date
    if start_date:
        df = df[df.index >= pd.to_datetime(start_date)]
        if df.empty:
            print(f"Warning: No data available after {start_date}")
            return
    
    ticker = os.path.basename(csv_path).split('_')[0]
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue', alpha=0.6)
    
    if op_dates:
        valid_ops = []
        # Get the timezone if any, or assume naive
        index_tz = df.index.tz
        
        for date_str in op_dates:
            try:
                op_date = pd.to_datetime(date_str)
                if index_tz:
                    op_date = op_date.tz_localize(index_tz)
                
                # Find nearest trading date; drop if more than 1 week away
                nearest_idx = df.index.get_indexer([op_date], method='nearest')[0]
                nearest_date = df.index[nearest_idx]
                if abs((nearest_date - op_date).days) > 7:
                    print(
                        f"Warning: No trading date within 1 week of {date_str}, skipping.")
                    continue
                valid_ops.append((nearest_date, df.loc[nearest_date, 'Close'], date_str))
            except Exception as e:
                print(f"Warning: Could not process date {date_str}: {e}")

        if valid_ops:
            op_x, op_y, labels = zip(*valid_ops)
            plt.scatter(op_x, op_y, color='red', s=10, label='Operations', zorder=5)

    plt.title(f"{ticker} Stock Price Visualization")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    chart_name = os.path.basename(csv_path).replace(
        '.csv', f'_chart_{start_date}.jpg')
    output_image = os.path.join(output_dir, chart_name)
    plt.savefig(output_image)
    print(f"Chart saved to {output_image}")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Visualize stock data from a local CSV file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the stock data CSV file")
    parser.add_argument("--ops", type=str, help="Path to a text file containing operation dates (one per line) or comma-separated dates.")
    parser.add_argument("--start", type=str, default="2019-07-15",
                        help="Start date for the graph (YYYY-MM-DD), default: 2019-07-15")
    parser.add_argument("--outdir", type=str, default="output",
                        help="Directory to save the output chart (default: output)")

    args = parser.parse_args()
    
    try:
        op_dates = []
        if args.ops:
            if os.path.exists(args.ops):
                with open(args.ops, 'r') as f:
                    # Read lines, strip whitespace, and ignore empty lines
                    op_dates = [line.strip() for line in f if line.strip()]
            else:
                # Fallback to comma-separated list
                op_dates = args.ops.split(',')
        
        plot_from_csv(args.input, op_dates, args.start, args.outdir)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
