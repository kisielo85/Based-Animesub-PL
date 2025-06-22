import requests
import re
from bs4 import BeautifulSoup


def search(txt):
    txt = txt.replace(" ", "+")
    results = {}

    for TITLE in ['org', 'en', 'pl']:  # każda wersja tytułu
        response = requests.get(
            f'http://animesub.info/szukaj.php?szukane={txt}&pTitle={TITLE}'
        )
        soup = BeautifulSoup(response.content, 'html.parser')

        data_segments = soup.find_all('table', class_='Napisy')

        for s in data_segments:
            sub_id = s.find('input', attrs={'name': 'id'})
            if not sub_id or sub_id in results:
                continue

            sub_id = sub_id['value']
            author_id = s.find('a')['href'][13:]
            author_txt = s.find('a').get_text()[1:]

            episode = s.find('td').get_text()
            episode_max = False

            # regex sprawdza czy to odcinek serialu czy film
            if re.search(r' ep\d+(?:-\d+)?$', episode):
                ep_pos = episode.rfind("ep")
                title = episode[: ep_pos - 1]
                episode = episode[ep_pos + 2 :]

                # '-' oznacza że w tym wyniku jest kilka odcinków
                if '-' in episode:
                    episode, episode_max = episode.split('-')
                    episode_max = int(episode_max)

                episode = int(episode)
            else:
                title = episode
                episode = False

            results[sub_id] = {
                'title': title,
                'author_id': author_id,
                'author_txt': author_txt,
                'episode': episode,
                'episode_max': episode_max,
            }
    return results


if __name__ == '__main__':
    from pprint import pprint

    result = search("bocchi the rock")
    pprint(result)
