import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import threading


def result_processing(lock, results, link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    data_segments = soup.find_all('table', class_='Napisy')
    if len(data_segments) <= 1:
        return False

    # elementy html z napisami
    for s in data_segments:
        sub_id = s.find('input', attrs={'name': 'id'})
        if not sub_id or sub_id in results:
            continue

        sub_id = sub_id['value']
        author_id = s.find('a')['href'][13:]
        author_txt = s.find('a').get_text()[1:]
        title = s.find('td').get_text()
        title_en = s.find_all('tr')[1].find('td').get_text()
        date = datetime.strptime(s.find_all('td')[1].get_text(), "%Y.%m.%d")
        episodes = []

        # jeśli to serial a nie film
        if re.search(r' ep\d+(?:-\d+)?$', title):
            # odzielenie tytułu od nr. odcinka
            ep_pos = title.rfind("ep")
            episode = title[ep_pos + 2 :]
            title = title[: ep_pos - 1]
            title_en = title_en[: title_en.rfind("ep") - 1]

            # '-' oznacza że w tym wyniku jest kilka odcinków
            if '-' in episode:
                episode, episode_max = episode.split('-')
                for i in range(int(episode), int(episode_max) + 1):
                    episodes.append(i)
            else:
                episodes = [int(episode)]
        
        key = title + "_" + author_id
        # lock żeby wątki nie zapisywały w tym samym czasie
        with lock:
            if key not in results:
                results[key] = {
                    'sub_results': [],
                    'title': title,
                    'title_en': title_en,
                    'author_id': author_id,
                    'author_txt': author_txt,
                }
            if not any(sr['id'] == sub_id for sr in results[key]['sub_results']):
                results[key]['sub_results'].append(
                    {
                        'id': sub_id,
                        'episodes': episodes,
                        'date': date,
                    }
                )
    return True


def search(txt):
    txt = txt.replace(" ", "+")
    lock = threading.Lock()
    results = {}

    # pobieranie wyników z animesub.info, zapis według autora i nazwy anime
    for TITLE in ['org', 'en', 'pl']:  # każda wersja tytułu
        page = 0
        while result_processing(
            lock,
            results,
            f'http://animesub.info/szukaj.php?szukane={txt}&pTitle={TITLE}&od={page}',
        ):
            page += 1

    batches = []

    def add_info(b, r):
        b['title'] = r['title']
        b['title_en'] = r['title_en']
        b['author'] = r['author_txt']
        b['author_id'] = r['author_id']
        return b

    for key in results:
        r = results[key]
        r['sub_results'] = sorted(r['sub_results'], key=lambda x: x['date'])

        batch = {'episodes': [], 'sub_ids': []}

        for sub in r['sub_results']:
            # jeśli odc sie pokrywają -> nowy batch
            if not set(batch['episodes']).isdisjoint(sub['episodes']):
                batches.append(add_info(batch, r))
                batch = {'episodes': [], 'sub_ids': []}

            batch['episodes'] += sub['episodes']
            batch['sub_ids'].append(sub['id'])

        batches.append(add_info(batch, r))

    return batches