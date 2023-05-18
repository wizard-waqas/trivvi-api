Upon clone, run `pip install -r requirements.txt` to install the required packages

To deploy new changes run `gcloud app deploy` from the root of the project

Url: `https://trivvi-6a057.uc.r.appspot.com/`

Routes:
- Youtube parsing `api/youtube/<video_id>`

- File upload `api/parsepdf`

- OpenAI API
  - generate tf quiz `api/ai-generate/tf`
  - generate mc quiz `api/ai-generate/mc`
  - generate key points `api/ai-generate/key-points`