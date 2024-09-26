# Artichoke Reader

Cloud Run Function scripts for text summary to audio MP3 conversion.



## Development


```sh

# Run locally
functions-framework-python --source summary.py --target summary --debug


# Test It
curl -X POST \
   -H 'Content-type: application/json' \
   0.0.0.0:8080 \
   -d '{"url": "https://ddrscott.github.io/blog/2024/recovering-10x-developer/"}'
```


## Deployment


```sh
gcloud functions deploy python-http-function \
--project=ilanes  \
--gen2 \
--runtime=python312 \
--region=us-central1 \
--source=summary.py \
--entry-point=summary \
--trigger-http \
--allow-unauthenticated
```
