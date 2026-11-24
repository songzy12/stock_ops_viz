python fetcher.py \
  --apikey APA0JJAVPPGECRBG \
  --ticker GOOG \
  --outdir data

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2019-07-15 \
  --ops input/ops.txt \
  --outdir output

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2023-03-24 \
  --ops input/ops.txt \
  --outdir output

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2024-03-28 \
  --ops input/ops.txt \
  --outdir output

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2025-08-15 \
  --ops input/ops.txt \
  --outdir output

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2025-10-17 \
  --ops input/ops.txt \
  --outdir output
