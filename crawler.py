import requests, re, html
from bs4 import BeautifulSoup
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

    print("\n✅ BOK 크롤링 완료!")
    print(f"총 {len(results)}건 수집됨\n")

    # 결과셋 터미널 출력(1000자)
    for r in results[:3]:
        print(f"• {r[0]} → {r[1][:1000]}")

def crawl_kdi():
    base_url = "https://eiec.kdi.re.kr/material/wordDicDetail.do?dic_idx="
    results = []

    for i in tqdm(range(1,10)):
        #url 세팅후 요청
        url = f"{base_url}{i}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
        if res.status_code != 200:
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        # 용어명 : <dt>
        term = soup.select_one("dt")
        term_txt = term.get_text(strip=True) if term else f"no_title_{i}"

        # 용어명 : <dd>
        desc = soup.select_one("dd")
        if desc:
            desc_txt = desc.get_text(strip=True)
            desc_short = ". ".join(desc_txt.split(". ")[:3]) + "."
        else:
            desc_short = ""


        # 결과 저장
        results.append((term_txt, desc_short))
        tqdm.write(f"{i}번 {term_txt}")
    
    print("\n✅ KDI 크롤링 완료!")
    print(f"총 {len(results)}건 수집됨\n")

    # 결과셋 터미널 출력(1000자)
    for r in results[:3]:
        print(f"• {r[0]} → {r[1][:4000]}")

if __name__ == "__main__":
    crawl_bok()
    crawl_kdi()
