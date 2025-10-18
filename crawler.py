import requests, re, html
from bs4 import BeautifulSoup
from tqdm import tqdm
import psycopg2
import os

def clean_txt(raw:str) -> str:
    text = html.unescape(raw)   # HTML 엔티티 복원
    text = re.sub(r"<[^>]+>", "", text)     # HTML 태그제거
    text = re.sub(r"\s+", " ", text)        # 공백정리
    return text.strip()

def save_to_db(data: list):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),  # 환경 변수에서 DB 정보 가져오기
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO keyword (term, description, source, link)
        VALUES (%s, %s, %s, %s)
    """
    cursor.executemany(insert_query, data)  # 여러 데이터를 한번에 저장

    conn.commit()
    cursor.close()
    conn.close()

def crawl_bok():
    base_url = "https://www.bok.or.kr/portal/ecEdu/ecWordDicary/searchCont.json?ecWordSn="
    results = []

    for i in tqdm(range(10, 101)):
        # url세팅후 요청
        res = requests.get(f"{base_url}{i}")
        if res.status_code != 200:
            tqdm.write(f"Error {res.status_code} at {i}")
            continue

        data = res.json().get("result")
        if not data:
            continue

        # 응답 데이터 파싱
        keyword = data.get("ecWordNm")
        desc = clean_txt(data.get("ecWordCn", ""))
        desc_short = ". ".join(desc.split(".")[:2]) + "."

        # 결과저장
        results.append((
            keyword,
            desc_short,
            "BOK(한국은행) 경제용어사전",
            "https://www.bok.or.kr/portal/ecEdu/ecWordDicary/search.do?menuNo=200688"
        ))
    
    save_to_db(results) # 한 번에 DB에 저장
    tqdm.write("\n✅ BOK 크롤링 완료!")
    print(f"총 {len(results)}건 수집됨\n")

def crawl_kdi():
    base_url = "https://eiec.kdi.re.kr/material/wordDicDetail.do?dic_idx="
    results = []

    for i in tqdm(range(10,101)):
        #url 세팅후 요청
        url = f"{base_url}{i}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
        if res.status_code != 200:
            tqdm.write(f"Error {res.status_code} at {i}")
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
        results.append((
            term_txt,
            desc_short,
            "KDI(한국개발연구원) 경제교육정보센터",
            "https://eiec.kdi.re.kr/material/wordDic.do"
        ))

    save_to_db(results)  # 한 번에 DB에 저장
    tqdm.write("\n✅ KDI 크롤링 완료!")
    print(f"총 {len(results)}건 수집됨\n")

if __name__ == "__main__":
    crawl_bok()
    crawl_kdi()
