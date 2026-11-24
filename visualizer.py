import argparse
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os


def find_valid_ops(df, op_dates):
    valid_ops = []
    for date_str in op_dates or []:
        try:
            op_date = pd.to_datetime(date_str)
            if df.index.tz:
                op_date = op_date.tz_localize(df.index.tz)

            nearest_idx = df.index.get_indexer([op_date], method='nearest')[0]
            nearest_date = df.index[nearest_idx]
            if abs((nearest_date - op_date).days) > 7:
                print(f"Warning: No trading date within 1 week of {date_str}, skipping.")
                continue
            valid_ops.append((nearest_date, df.loc[nearest_date, 'Close'], date_str))
        except Exception as e:
            print(f"Warning: Could not process date {date_str}: {e}")
    return valid_ops


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

    if df.empty:
        print("Warning: No data available")
        return

    ticker = os.path.basename(csv_path).split('_')[0]
    os.makedirs(output_dir, exist_ok=True)

    all_ops = find_valid_ops(df, op_dates)
    interactive_chart = go.Figure()
    interactive_chart.add_trace(go.Scatter(
        x=df.index, y=df['Close'], mode='lines', name='Close Price',
        line=dict(color='blue'), opacity=0.6,
        hovertemplate='%{x|%Y-%m-%d}<br>Close: $%{y:.2f}<extra></extra>',
    ))
    if all_ops:
        op_x, op_y, _ = zip(*all_ops)
        interactive_chart.add_trace(go.Scatter(
            x=op_x, y=op_y, mode='markers', name='Operations',
            marker=dict(color='lightcoral', size=4), hoverinfo='skip',
        ))
    interactive_chart.update_layout(
        title=f"{ticker} Stock Price Visualization",
        xaxis_title="Date", yaxis_title="Price (USD)", hovermode='x',
        xaxis=dict(
            showspikes=True, spikemode="across", spikesnap="cursor",
            spikedash="dot", spikethickness=1,
            autorangeoptions=(
                dict(clipmin=df.index.min(), clipmax=df.index.max())
                if df.index.min() != df.index.max() else None
            ),
            range=(
                [max(df.index.min(), df.index.max() - pd.DateOffset(years=8)), df.index.max()]
                if df.index.min() != df.index.max() else None
            ),
            rangeselector=dict(buttons=[
                dict(label="All", step="all"),
                dict(count=8, label="8 years", step="year", stepmode="backward"),
                dict(count=4, label="4 years", step="year", stepmode="backward"),
                dict(count=2, label="2 years", step="year", stepmode="backward"),
            ]),
        ),
    )
    output_html = os.path.join(
        output_dir, os.path.basename(csv_path).replace('.csv', '_chart.html'))
    interactive_chart.write_html(
        output_html, include_plotlyjs=True,
        post_script="""
        const chart = document.getElementById('{plot_id}');
        let activeMarkers = new Set();
        function clearMarkers() {
            for (const marker of activeMarkers) marker.style.fill = 'lightcoral';
            activeMarkers.clear();
        }
        chart.addEventListener('pointermove', event => {
            const trace = chart._fullData.find(item => item.name === 'Operations');
            const plot = chart.querySelector('.nsewdrag');
            if (!trace || trace.visible !== true || !plot) {
                clearMarkers();
                return;
            }
            const plotBounds = plot.getBoundingClientRect();
            if (event.clientX < plotBounds.left || event.clientX > plotBounds.right ||
                event.clientY < plotBounds.top || event.clientY > plotBounds.bottom) {
                clearMarkers();
                return;
            }
            const markers = chart.querySelectorAll('.scatterlayer .trace' + trace.uid + ' .point');
            const matching = new Set();
            for (const marker of markers) {
                const bounds = marker.getBoundingClientRect();
                const x = (bounds.left + bounds.right) / 2;
                if (x >= plotBounds.left && x <= plotBounds.right &&
                    Math.abs(event.clientX - x) <= 4) {
                    matching.add(marker);
                }
            }
            for (const marker of activeMarkers) {
                if (!matching.has(marker)) marker.style.fill = 'lightcoral';
            }
            for (const marker of matching) {
                if (!activeMarkers.has(marker)) {
                    marker.style.fill = 'darkred';
                }
            }
            activeMarkers = matching;
        });
        chart.addEventListener('pointerleave', clearMarkers);
        chart.on('plotly_afterplot', clearMarkers);
        """,
    )
    print(f"Interactive chart saved to {output_html}")

    # The start date applies only to the JPG.
    if start_date:
        filtered_df = df[df.index >= pd.to_datetime(start_date)]
        if filtered_df.empty:
            print(f"Warning: No data available after {start_date}")
            return
    else:
        filtered_df = df

    valid_ops = all_ops if len(filtered_df) == len(df) else find_valid_ops(filtered_df, op_dates)
    plt.figure(figsize=(12, 6))
    plt.plot(filtered_df.index, filtered_df['Close'], label='Close Price', color='blue', alpha=0.6)

    if valid_ops:
        op_x, op_y, labels = zip(*valid_ops)
        plt.scatter(op_x, op_y, color='red', s=10, label='Operations', zorder=5)

    plt.title(f"{ticker} Stock Price Visualization")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    chart_name = os.path.basename(csv_path).replace(
        '.csv', f'_chart_{start_date}.jpg')
    output_image = os.path.join(output_dir, chart_name)
    plt.savefig(output_image)
    print(f"Chart saved to {output_image}")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Visualize stock data from a local CSV file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the stock data CSV file")
    parser.add_argument("--ops", type=str, help="Path to a text file containing operation dates (one per line) or comma-separated dates.")
    parser.add_argument("--start", type=str, default="2019-07-15",
                        help="Start date for the JPG (YYYY-MM-DD), default: 2019-07-15")
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
