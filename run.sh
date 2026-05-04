python fetcher.py \
  --apikey APA0JJAVPPGECRBG \
  --ticker GOOG \
  --outdir data
  
python visualizer.py \
  --input data/GOOG_data.csv \
  --start 2024-01-01 \
  --ops input/ops.txt \
  --outdir output
