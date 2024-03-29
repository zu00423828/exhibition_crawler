import re
import os
import time
import requests
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
from multiprocessing import Pool
month_format = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
Category = {"Agriculture & Forestry": "agriculture-forestry", "Animals & Pets": "animals-pets", "Apparel & Clothing": "apparel-fashion",
            "Arts & Crafts": "arts-crafts", "Auto & Automotive": "automotive", "Baby, Kids & Maternity": "baby-kids",
            "Banking & Finance": "finance", "Building & Construction": "building-construction", "Business Services": "business-consultancy",
            "Education & Training": "education-training", "Electric & Electronics": "electronics-electricals", "Entertainment & Media": "entertainment",
            "Environment & Waste": "waste-management", "Fashion & Beauty": "fashion-accessories", "Food & Beverages": "food-beverage",
            "Home & Office": "home-office", "Hospitality": "hospitality", "It & Technology": "technology",
            "Industrial Engineering": "engineering", "Logistics & Transportation": "logistics-transportation", "Medical & Pharma": "medical-pharma",
            "Miscellaneous": "trade-promotion", "Packing & Packaging": "packaging", "Power & Energy": "power-energy",
            "Science & Research": "research", "Security & Defense": "security", "Telecommunication": "telecommunication",
            "Travel & Tourism": "travel-tourism", "Wellness, Health & Fitness": "wellness-healthcare"
            }


# //*[@id = "content"]/tr[1]

def process_location(location):
    temp = location.replace("Get Directions", "").rsplit(", ", 1)
    return temp


def process_date(date):
    date_format = date.strip().replace("  ", " ").split(" ")
    year = date_format[-1]
    if len(date_format) == 5:
        start_month = month_format[date_format[1]]
        end_month = month_format[date_format[3]]
        start_day = date_format[0]
        end_day = date_format[2]
    else:
        start_month = month_format[date_format[2]]
        end_month = start_month
        start_day = date_format[0]
        end_day = date_format[1]
    return f"{year}-{start_month}-{start_day}", f"{year}-{end_month}-{end_day}"


# def get_logo(soup: BeautifulSoup):
#     #online-header-left > div > div.me-3 > img

#     # result = soup.find(
#     #     class_="img-thumbnail img-130 lazyload")
#     results = soup.select("img.img-thumbnail.img-130.lazyload")
#     # print(type(result))
#     if len(results) < 1:
#         results = soup.select("img.img-thumbnail.mt-1.lazyload")
#         if len(results) < 1:
#             return ""
#         return results[0].get("data-src")
#     # return result.get("src")
#     return results[0].get("src")

def get_logo(soup: BeautifulSoup):
    results = soup.find("img", alt="logo")
    url = results.get(
        "data-src") if "default.png" in results.get("src") else results.get("src")
    return url


def process_content(url, category, ua):
    event_name, \
        event_date_from, \
        event_date_to, \
        event_venue, \
        event_country, \
        event_paragraph_emphasis, \
        event_paragraph_content, \
        event_logo_url, \
        detail_time, \
        detail_fee, \
        detail_visitors, \
        detail_exhibitors, \
        detail_categories, \
        frequency_type, \
        venue_name, \
        venue_address = [""]*16

    headers = {'user-agent': ua.random}
    res = requests.get(url, headers)
    soup = BeautifulSoup(res.text, "lxml")
    try:
        event_name = soup.find("h1").text
    except:
        pass
    try:
        event_logo_url = get_logo(soup)
    except:
        pass
    try:

        items = soup.find_all(class_="mb-0 fs-20")
        if len(items) < 1:
            date_text = soup.select(
                "#online-header-left > div > div.w-100 > div.header_date.position-relative.text-orange > span:nth-child(1)")
            event_date = date_text[0].text.replace("-", '')
            event_date_from,  event_date_to = process_date(event_date)
            event_location = soup.select(
                "#online-header-left > div > div.w-100 > div:nth-child(4)")[0].text
            if "Get Directions" not in event_location:
                event_location = soup.select(
                    "#online-header-left > div > div.w-100 > div:nth-child(5)")[0].text
            event_venue, event_country = process_location(event_location)
        else:
            event_date = items[0].find_all("span")[1].text
            event_date = event_date.replace('-', '')
            event_date_from,  event_date_to = process_date(event_date)
            event_venue, event_country = process_location(items[1].text)
    except:
        pass
    # pavilion_name, city, country = process_location(items[1].text)
    try:
        event_paragraph_emphasis, event_paragraph_content = soup.find(
            class_="mng text-break fs-14").text.strip().replace("\"", "", 1).split("\"")
    except:
        pass
    try:
        detail_time = soup.find("tr", id="hvrout1").find_all(
            "td")[0].text.replace("Timings", "").replace("  ", "").strip() .replace("\n", "")
    except:
        pass
    try:
        detail_fee = soup.find("tr", id="hvrout1").find_all(
            "td")[1].text.replace("Entry Fees", "").replace("Check Official Website", "").replace("  ", " ").replace("\n", "").strip()
    except:
        pass
    try:
        numbers = soup.find(
            "table", class_="table noBorder mng w-100 trBorder").find_all("a", class_="text-decoration-none")
        detail_visitors = numbers[0].text.strip()
        detail_exhibitors = numbers[1].text.strip()
    except:
        pass
    # try:
    #     detail_categories = [item.text for item in soup.find("td", id="hvrout2").find_all(
    #         "a", class_="text-decoration-none")]
    # except:
    #     pass
    try:
        frequency_type = soup.find("tr", id="hvrout3").find(
            "td").text.split("Frequency")[-1].strip()
    except:
        pass
    try:
        venue_name = soup.find(
            class_="mb-1 fs-16").find(class_="text-decoration-none").text.replace("\n", "").strip()
    except:
        pass
        if venue_name == "":
            venue_name = event_venue.rsplit(",")[0].strip()
    try:
        # venue_address = soup.find(
        #     "section", class_="box map_dir").find("p").text
        venue_address_item = soup.find(
            "section", class_="box map_dir").find("p")
        # venue_address_clear = str(venue_address_item).replace("<p>", "").replace(
        #     "</p>", "").replace("<br>", "").replace("<br/>", '').replace("<span>", "")
        # venue_address = " ".join(venue_address_clear.split("</span>")).strip()
        venue_address = re.sub(
            "<p>|</p>|<span>|</span>|<br>|<br/>", " ", str(venue_address_item)).replace("  ", " ").strip()
    except:
        pass
    content = {
        "event_name": event_name,
        "event_date_from": event_date_from,
        "event_date_to": event_date_to,
        "event_venue": event_venue,
        "event_country": event_country,
        "event_paragraph_emphasis": event_paragraph_emphasis,
        "event_paragraph_content": event_paragraph_content,
        "event_logo_url": event_logo_url,
        "detail_time": detail_time,
        "detail_fee": detail_fee,
        "detail_visitors": detail_visitors,
        "detail_exhibitors": detail_exhibitors,
        "detail_categories": category,
        "frequency_type": frequency_type,
        "venue_name": venue_name,
        "venue_address": venue_address,
    }
    return content


def process(url, category):
    ip = "20.159.154.112:8080"
    proxy = {'http': ip, 'https': ip}
    proxy = None
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")
    top100_list = soup.findAll("a", class_="text-decoration-none me-2")
    # print(len(top100_list))
    json_data = []
    # ua = UserAgent()
    for item in tqdm(top100_list):
        # print(item.get("href"))
        data = process_content(item.get("href"), category, ua)
        json_data.append(data)
        time.sleep(0.3)
    return json_data


def mulit_crawler(data):
    key = data[0]
    item = data[1]
    if os.path.exists(f"out/{item}.json"):
        return
    print(key, item)
    # res = requests.get(f"https://10times.com/top100/{item}")
    print("hi")
    json_data = process(f"https://10times.com/top100/{item}", key)
    print("hi2")
    json_object = json.dumps(json_data)
    with open(f"out/{item}.json", 'a') as f:
        f.write(json_object)
    return 1


def mulit_main():
    pool = Pool(4)
    pool_outputs = pool.map(mulit_crawler, Category.items())
    print('將不會阻塞並和 pool.map_async 並行觸發')

    # close 和 join 是確保主程序結束後，子程序仍然繼續進行
    pool.close()
    pool.join()


def main():
    root = "https://10times.com/top100/"
    print(len(Category))
    for key, item in Category.items():
        if os.path.exists(f"out/{item}.json"):
            continue
        print(key, item)
        # res = requests.get(f"https://10times.com/top100/{item}")
        json_data = process(f"https://10times.com/top100/{item}", key)
        json_object = json.dumps(json_data)
        with open(f"out/{item}.json", 'a') as f:
            f.write(json_object)
        # break
        # print(res.status_code)


if __name__ == "__main__":
    ua = UserAgent()
    main()
    # mulit_main()
