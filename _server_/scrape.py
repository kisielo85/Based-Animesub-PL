import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import threading
from difflib import SequenceMatcher
import os
import zipfile
import py7zr
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import shutil


# zbieranie danych z html
def result_processing(lock, results, link, pages=False, title_mode=False):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "lxml")
    data_segments = soup.find_all("table", class_="Napisy")
    if len(data_segments) <= 1:
        return False

    # sprawdzanie liczby stron
    if pages != False:
        pages_elements = soup.find_all("a", class_="StrWKat")
        if pages_elements == []:
            pages[title_mode] = 1
        else:
            pages[title_mode] = int(pages_elements[-1].get_text().replace(".", ""))

    # elementy html z napisami
    for s in data_segments:
        sub_id = s.find("input", attrs={"name": "id"})
        if not sub_id or sub_id in results:
            continue

        sub_id = sub_id["value"]
        author_id = s.find("a")["href"][13:]
        author_txt = s.find("a").get_text()[1:]
        title = s.find("td").get_text()
        title_en = s.find_all("tr")[1].find("td").get_text()
        date = datetime.strptime(s.find_all("td")[1].get_text(), "%Y.%m.%d").strftime("%Y-%m-%d")
        description = (
            s.find("tr", class_="KKom")
            .find("td", class_="KNap")
            .get_text(separator="<br>", strip=True)
            .replace("Autor:<br>", "Autor: ")
        )
        episodes = []

        # jeśli to serial a nie film
        if re.search(r" ep\d+(?:-\d+)?$", title):
            # odzielenie tytułu od nr. odcinka
            ep_pos = title.rfind("ep")
            episode = title[ep_pos + 2 :]
            title = title[: ep_pos - 1]
            title_en = title_en[: title_en.rfind("ep") - 1]

            # '-' oznacza że w tym wyniku jest kilka odcinków
            if "-" in episode:
                episode, episode_max = episode.split("-")
                for i in range(int(episode), int(episode_max) + 1):
                    episodes.append(i)
            else:
                episodes = [int(episode)]

        key = title + "_" + author_id
        # lock żeby wątki nie zapisywały w tym samym czasie
        with lock:
            if key not in results:
                results[key] = {
                    "sub_results": [],
                    "title": title,
                    "title_en": title_en,
                    "author_id": author_id,
                    "author_txt": author_txt,
                }
            if not any(sr["id"] == sub_id for sr in results[key]["sub_results"]):
                results[key]["sub_results"].append(
                    {
                        "id": sub_id,
                        "episodes": episodes,
                        "date": date,
                        "description": description,
                    }
                )

    # sortowanie po id
    for key in results:
        results[key]["sub_results"] = sorted(results[key]["sub_results"], key=lambda x: x["id"])

    return True


# szukanie napisów z animesub.info
def search(txt):
    txt = txt.replace(" ", "+")
    lock = threading.Lock()
    results = {}
    pages = {"org": 0, "en": 0, "pl": 0}

    # pobieranie wyników z animesub.info, zapis według autora i nazwy anime
    # na początek tylko pierwsze strony z każdego rodzaju tytułu aby sprawdzić ilośc stron
    with ThreadPoolExecutor(max_workers=3) as executor:
        for TITLE in ["org", "en", "pl"]:
            executor.submit(
                result_processing,
                lock,
                results,
                f"http://animesub.info/szukaj.php?szukane={txt}&pTitle={TITLE}",
                pages,
                TITLE,
            )

    # zapis linków do sprawdzenia
    links = []
    for p in pages:
        for i in range(1, pages[p]):
            links.append(f"http://animesub.info/szukaj.php?szukane={txt}&pTitle={p}&od={i}")

    # przeszukanie linków
    with ThreadPoolExecutor(max_workers=8) as executor:
        for link in links:
            executor.submit(result_processing, lock, results, link)

    batches = []

    def add_info(b, r):
        b["title"] = r["title"]
        b["title_en"] = r["title_en"]
        b["author"] = r["author_txt"]
        b["author_id"] = r["author_id"]
        return b

    for key in results:
        r = results[key]
        r["sub_results"] = sorted(r["sub_results"], key=lambda x: x["date"])

        batch = {
            "episodes": [],
            "sub_ids": [],
            "descriptions": [],
            "date": "0000-00-00",
        }

        for sub in r["sub_results"]:
            # jeśli odc sie pokrywają -> nowy batch
            if not set(batch["episodes"]).isdisjoint(sub["episodes"]):
                batches.append(add_info(batch, r))
                batch = {
                    "episodes": [],
                    "sub_ids": [],
                    "descriptions": [],
                    "date": "0000-00-00",
                }

            if sub["date"] > batch["date"]:
                batch["date"] = sub["date"]
            batch["episodes"] += sub["episodes"]
            batch["sub_ids"].append(sub["id"])
            batch["descriptions"].append(sub["description"])

        batches.append(add_info(batch, r))

    batches = sorted(
        batches,
        reverse=True,
        key=lambda x: (
            SequenceMatcher(None, txt, x["title"]).ratio()
            + SequenceMatcher(None, txt, x["title_en"]).ratio(),
            len(x["episodes"]),
            x["date"],
        ),
    )

    return batches


def download_file(id, job, files):
    # jeśli nie uda sie pobrać, to próbuje jeszcze kilka razy
    for i in range(5):
        try:
            response = requests.post("http://animesub.info/sciagnij.php", data={"id": id})
            if response.ok:
                break
        finally:
            if i >= 4:
                job['failed'] = True
                return
            sleep(1)

    # zapis pobranego zip
    filename = f"{job['path']}/{id}.zip"
    with open(filename, "wb") as f:
        f.write(response.content)
    files.append([filename, response.content[:2], response.headers.get("Content-Disposition")])
    job['done'] += 4


# pobieranie danych napisów
def download(ids, job):
    path = "./cache/" + "_".join(str(i) for i in ids)
    os.makedirs(path + "/result", exist_ok=True)
    job['path'] = path
    job['done'] = 0
    job['done_max'] = len(ids) * 5 + 1
    job['failed'] = False

    output_name = ""
    files = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for id in ids:
            executor.submit(download_file, id, job, files)

    if job['failed']:
        return False

    for filename, zip_mode, default_name in files:
        # rozpakowywanie
        match (zip_mode):
            case b"PK":  # zip
                with zipfile.ZipFile(filename, "r") as archive:
                    archive.extractall(f"{path}/extracted")
            case b"7z":  # 7zip
                with py7zr.SevenZipFile(filename, mode="r") as archive:
                    archive.extractall(f"{path}/extracted")
            case "_":
                print("nie można wypakować pliku")
                return (False, False)

        job['done'] += 1

        # nazwa zipa z wynikiem
        if output_name == "":
            output_name = "plik_BasedAnimesubInfo.zip"  # fallback

            # domyślna nazwa pobranego pliku
            if not default_name:
                continue
            match = re.search(r'filename="?([^"]+)"?', default_name)
            if not match:
                continue

            # usunięcie _ep**_ i dodanie Based
            output_name = match.group(1)
            output_name = re.sub(r"_ep\d+(_\d+)?_", "_", output_name)
            output_name = output_name.replace("_AnimeSubInfo_id", "_BasedAnimeSubInfo_")

    output_path = f"{path}/result/{output_name}"
    # pakowanie wszystkich napisów do jednego pliku
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(f"{path}/extracted"):
            for file in files:
                if file.lower().endswith((".zip", ".7z")):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=f"{path}/extracted")
                zipf.write(file_path, arcname)

    job['done'] = job['done_max']
    job['result_path'] = output_path
    job['result_name'] = output_name

    # usuwanie niepotrzebnych plików
    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        if item == 'result':
            continue
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def start_download(ids, job):
    t = threading.Thread(target=download, args=(ids, job))
    t.start()
