import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm, trange


def get_data(url) -> dict:
    output = {"exhibition_name": None, "exhibition_logo_url": None, "exhibition_description": None,
              "exhibition_cycle": None, "exhibition_date": None, "exhibition_city": None, "exhibition_country": None,
              "venue_name": None, "venue_address": None, "organizer_name": None, "offical_website": None}
    init = [""]*11
    exhibition_name, exhibition_logo_url, exhibition_description, exhibition_cycle, exhibition_date, exhibition_city, exhibition_country = init[
        :-4]
    venue_name, venue_address, organizer_name, offical_website = init[-4:]
    # url = "https://www.eventseye.com/fairs/f-united-dairy-tech-26546-1.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "lxml")
    try:
        exhibition_name = soup.find("h1").text
    except:
        pass
    try:
        exhibition_logo_url = web_root + soup.find("img").get("src")
    except:
        pass
    try:
        exhibition_description = soup.find(
            class_="description").text.replace("Description", "").strip()
    except:
        pass
    try:
        exhibition_cycle = soup.find(
            class_="cycle").text.replace("Cycle", "").strip()
    except:
        pass
    try:
        date_content = soup.find(class_="dates").find_all("td")
        exhibition_date = date_content[0].text.strip()
        exhibition_city, exhibition_country = date_content[1].text.strip()[::-1].replace(")", "", 1)[::-1].rsplit(
            " (", 1)
    except:
        pass
    try:
        venue_name = date_content[2].text.strip()
        venue_context = soup.find(class_="venue").find(
            class_="info").find(class_="text")
        venue_context = venue_context.text.split("\n")
        address_contents = [content.strip() for content in venue_context[2:-6]]
        address = " ".join(address_contents)
        venue_address = address
    except:
        pass
    try:
        organizer_context = soup.find(class_="orgs").find(
            class_="info").find(class_="text")
        organizer_context = organizer_context.text.split("\n")
        organizer_name = organizer_context[1]
    except:
        pass
    try:
        offical_website = soup.find(class_="more-info").find("a").get("href")
    except:
        pass
    output = {"exhibition_name": exhibition_name, "exhibition_logo_url": exhibition_logo_url, "exhibition_description": exhibition_description,
              "exhibition_cycle": exhibition_cycle, "exhibition_date": exhibition_date, "exhibition_city": exhibition_city, "exhibition_country": exhibition_country,
              "venue_name": venue_name, "venue_address": venue_address, "organizer_name": organizer_name, "offical_website": offical_website}
    return output


if __name__ == "__main__":
    web_root = "https://www.eventseye.com"

    zooms = ["z1_trade-shows_asia-pacific.html", "z1_trade-shows_europe.html",
             "z1_trade-shows_africa-middle-east.html", "z1_trade-shows_america.html"]
    json_data = []
    for zoom in tqdm(zooms):
        web_url = web_root + "/fairs/" + zoom
        res = requests.get(web_url)
        soup = BeautifulSoup(res.text, "lxml")
        page_num = soup.find(class_="pagenum").text.split("/")[-1]
        results = soup.find(class_="tradeshows").find_all("tr")
        for result in results[1:]:
            link = result.find("td").find("a").get("href")
            complete_link = web_root+"/fairs/" + link
            json_data.append(get_data(complete_link))

        for page in trange(1, int(page_num)):
            url = web_url.replace(".html", f"_{page}.html")
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "lxml")
            results = soup.find(class_="tradeshows").find_all("tr")
            for result in results[1:]:
                link = result.find("td").find("a").get("href")
                complete_link = web_root+"/fairs/" + link
                json_data.append(get_data(complete_link))
    json_object = json.dumps(json_data)
    with open("data.json", "w") as f:
        f.write(json_object)
