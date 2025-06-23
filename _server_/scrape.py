import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime


def search(txt):
    txt = txt.replace(" ", "+")
    results = {}

    # pobieranie wyników z animesub.info, zapis według autora i nazwy anime
    for TITLE in ['org', 'en', 'pl']:  # każda wersja tytułu
        page = 0
        while True:
            response = requests.get(
                f'http://animesub.info/szukaj.php?szukane={txt}&pTitle={TITLE}&od={page}'
            )
            page += 1
            soup = BeautifulSoup(response.content, 'html.parser')
            data_segments = soup.find_all('table', class_='Napisy')
            if len(data_segments) <= 1:
                break

            for s in data_segments:
                sub_id = s.find('input', attrs={'name': 'id'})
                if not sub_id or sub_id in results:
                    continue

                sub_id = sub_id['value']
                author_id = s.find('a')['href'][13:]
                author_txt = s.find('a').get_text()[1:]
                date = datetime.strptime(s.find_all('td')[1].get_text(), "%Y.%m.%d")

                episode = s.find('td').get_text()
                episode_max = False
                episodes = []

                # regex sprawdza czy to odcinek serialu czy film
                if re.search(r' ep\d+(?:-\d+)?$', episode):
                    ep_pos = episode.rfind("ep")
                    title = episode[: ep_pos - 1]
                    episode = episode[ep_pos + 2 :]

                    # '-' oznacza że w tym wyniku jest kilka odcinków
                    if '-' in episode:
                        episode, episode_max = episode.split('-')
                        episode_max = int(episode_max)
                        for i in range(int(episode), episode_max + 1):
                            episodes.append(i)
                    else:
                        episodes = [int(episode)]
                else:
                    title = episode
                    episode = False

                key = title + "_" + author_id
                if key not in results:
                    results[key] = {
                        'sub_results': [],
                        'title': title,
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

    batches = []

    def add_info(b, r):
        b['title'] = r['title']
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


if __name__ == '__main__':
    from pprint import pprint

    result = search("steins gate")
    for g in result:
        pprint(g)
        print("\n\n\n")
