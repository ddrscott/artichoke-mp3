# Artichoke Reader

Cloud Run Function scripts for text summary to audio MP3 conversion.


## Usage

```sh
curl -X POST \
   -H 'Content-type: application/json' \
   https://us-central1-ilanes.cloudfunctions.net/artichoke-summary \
   -d '{"url": "https://ddrscott.github.io/blog/2018/stream-stats-in-rust/"}'

```

### Output
```json
{
  "url": "https://ddrscott.github.io/blog/2018/stream-stats-in-rust/",
  "voice": "nova",
  "script": "Ever felt like you were missing out on the cool stuff happening in the tech world? \ud83d\udcbb  Well, listen up, because this episode dives deep into a program called \"stream_stats\" and how it can make your tech life way easier.  This little program acts like a super-powered version of the `cat` command that you already know and love. Not only can it print stuff out, but it can count lines and even tell you how fast things are moving. And get this, it even includes a handy-dandy buffer so you can handle massive amounts of data.  So, if you're looking to up your coding game and gain a deeper understanding of how your tech works, stream_stats is your new best friend.  \n",
  "mp3": "https://cdn.dataturd.com/artichoke/summary/26b4071781b94e4b17743439c8652ec3.mp3"
  }
```

## Development

```sh

# Run locally
functions-framework-python --target summary --debug


# Test It
curl -X POST \
   -H 'Content-type: application/json' \
   0.0.0.0:8080 \
   -d '{"url": "https://ddrscott.github.io/blog/2024/recovering-10x-developer/"}'
```


## Deployment


```sh
gcloud functions deploy artichoke-summary \
--project=ilanes  \
--gen2 \
--runtime=python312 \
--region=us-central1 \
--entry-point=summary \
--trigger-http \
--allow-unauthenticated
```
