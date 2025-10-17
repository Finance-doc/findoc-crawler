import requests, re, html
from tqdm import tqdm

def clean_txt(raw:str) -> str:
    text = html.unescape(raw)   # HTML 엔티티 복원
    text = re.sub(r"<[^>]+>", "", text)     # HTML 태그제거
    text = re.sub(r"\s+", " ", text)        # 공백정리
    return text.strip()

def crawl_bok():
    base_url = "https://www.bok.or.kr/portal/ecEdu/ecWordDicary/searchCont.json?ecWordSn="
    results = []

    for i in tqdm(range(1, 10)):
        # url세팅후 요청
        res = requests.get(f"{base_url}{i}")
        if res.status_code != 200:
            continue

        data = res.json().get("result")
        if not data:
            continue

        # 응답 데이터 파싱후 결과셋에 추가
        keyword = data.get("ecWordNm")
        desc = clean_txt(data.get("ecWordCn", ""))
        desc_short = ". ".join(desc.split(".")[:2]) + "."

        results.append((keyword, desc_short))
        tqdm.write(f"{i}번 {keyword}")  # tqdm-safe 출력

    print("\n✅ 크롤링 완료!")
    print(f"총 {len(results)}건 수집됨\n")

    # 결과셋 터미널 출력(1000자)
    for r in results[:3]:
        print(f"• {r[0]} → {r[1][:1000]}...")

if __name__ == "__main__":
    crawl_bok()
