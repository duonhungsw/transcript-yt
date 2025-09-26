from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from urllib.parse import urlparse, parse_qs
# import eng_to_ipa as ipa
import itertools
from youtube_transcript_api.proxies import GenericProxyConfig

app = FastAPI()

class UrlRequest(BaseModel):
    videoId: str

def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        return qs.get("v", [None])[0]
    return url  # fallback: nếu user truyền thẳng videoId

# List proxy free bạn có
proxies = [
    "142.111.48.253:7030",
    "198.23.239.134:6540",
    "45.38.107.97:6014",
    "107.172.163.27:6543",
    "64.137.96.74:6641",
    "154.203.43.247:5536",
    "84.247.60.125:6095",
    "216.10.27.159:6837",
    "142.111.67.146:5611",
    "142.147.128.93:6593"
]

username = "caeuoxgs"
password = "mws74sumq7d0"

proxy_cycle = itertools.cycle(proxies)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/transcript")
def get_transcript(request: UrlRequest, lang: str = "vi"):
    # bạn có thể extract video_id từ request nếu muốn, ở đây hardcode để test
    # video_id = "tLwyHs7oXGM"
    proxy = next(proxy_cycle)
    proxy_url = f"http://{username}:{password}@{proxy}"
    print(request.videoId)
    video_id = request.videoId
    try:
    #     ytt_api = YouTubeTranscriptApi(proxy_config=GenericProxyConfig(
    #     http_url="http://zbtlapzo:rb0z3okzq8tv@142.111.48.253/",
    #     https_url="http://zbtlapzo:rb0z3okzq8tv@142.111.48.253/",
    # ))
        # ytt_api = YouTubeTranscriptApi(proxy_config=WebshareProxyConfig(
        # proxy_username="caeuoxgs",
        # proxy_password="mws74sumq7d0",
        #     )
        # )
        
        ytt_api = YouTubeTranscriptApi(
        proxy_config=GenericProxyConfig(
            http_url=proxy_url,
            https_url=proxy_url,
            )
        )
        transcript_list = ytt_api.list(video_id)

        transcript = transcript_list.find_transcript(["en"])

        # Fetch bản gốc (EN)
        original = transcript.fetch().to_raw_data()

        # Fetch bản dịch (VN) nếu có
        translated = None
        if transcript.is_translatable and any(l.language_code == "vi" for l in transcript.translation_languages):
            translated = transcript.translate("vi").fetch().to_raw_data()

        # Ghép song song EN + VN
        result = []
        for idx, item in enumerate(original):
            vn_text = None
            if translated and idx < len(translated):
                vn_text = translated[idx]["text"]
                # ipa_text = ipa.convert(item["text"]) if item["text"] else None

            result.append({
                "orderIndex": idx + 1,
                "startTime": item["start"],
                "endTime": item["start"] + item["duration"],
                "contentEN": item["text"],
                "contentVN": vn_text,
                # "ipa": ipa_text
            })

        return result

    except Exception as e:
        import traceback
        print("Error:", str(e))
        traceback.print_exc()
        return {"error": str(e)}
    
@app.post("/transcript-example")
def get_transcript(request: UrlRequest, lang: str = "vi"):
    # bạn có thể extract video_id từ request nếu muốn, ở đây hardcode để test
    video_id = "tLwyHs7oXGM"
    # print(request.videoId)
    # video_id = request.videoId
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        transcript = transcript_list.find_transcript(["en"])

        # Fetch bản gốc (EN)
        original = transcript.fetch().to_raw_data()

        # Fetch bản dịch (VN) nếu có
        translated = None
        if transcript.is_translatable and any(l.language_code == "vi" for l in transcript.translation_languages):
            translated = transcript.translate("vi").fetch().to_raw_data()

        # Ghép song song EN + VN
        result = []
        for idx, item in enumerate(original):
            vn_text = None
            if translated and idx < len(translated):
                vn_text = translated[idx]["text"]
                # ipa_text = ipa.convert(item["text"]) if item["text"] else None

            result.append({
                "orderIndex": idx + 1,
                "startTime": item["start"],
                "endTime": item["start"] + item["duration"],
                "contentEN": item["text"],
                "contentVN": vn_text,
                # "ipa": ipa_text
            })

        return result + video_id

    except Exception as e:
        import traceback
        print("Error:", str(e) + video_id)
        traceback.print_exc()
        return {"error": str(e) + video_id}