python fetcher.py \
  --apikey APA0JJAVPPGECRBG \
  --ticker GOOG \
  --outdir data
  
python visualizer.py \
  --input data/GOOG_data.csv \
  --ops input/ops.txt \
  --outdir output
