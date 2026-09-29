python fetcher.py \
  --apikey APA0JJAVPPGECRBG \
  --ticker GOOG \
  --outdir data

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2019-04-22 \
  --ops input/ops.txt \
  --outdir output

python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2025-04-22 \
  --ops input/ops.txt \
  --outdir output
