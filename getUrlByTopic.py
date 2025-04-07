import json
import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError

base_url = "https://www.zhihu.com/api/v5.1/topics/URLID/feeds/essence/v2"

def get_topic_id(url):
    return url.split('/')[-1]

def main():
    with open('topic_links.txt', 'r', encoding='utf-8') as file:
        topic_links = file.readlines()

    try:
        with open('topic_answer_links.txt', 'r', encoding='utf-8') as file:
            existing_answer_links = set(line.split(' ')[0] for line in file.read().splitlines())
    except FileNotFoundError:
        existing_answer_links = set()

    try:
        with open('topic_question_links.txt', 'r', encoding='utf-8') as file:
            existing_question_links = set(line.split(' ')[0] for line in file.read().splitlines())
    except FileNotFoundError:
        existing_question_links = set()

    try:
        with open('topic_article_links.txt', 'r', encoding='utf-8') as file:
            existing_article_links = set(line.split(' ')[0] for line in file.read().splitlines())
    except FileNotFoundError:
        existing_article_links = set()

    with open('topic_answer_links.txt', 'a', encoding='utf-8') as answer_output_file, \
         open('topic_article_links.txt', 'a', encoding='utf-8') as article_output_file, \
         open('topic_question_links.txt', 'a', encoding='utf-8') as question_output_file:
        for link in topic_links:
            topic_id = get_topic_id(link.strip())
            url = base_url.replace('URLID', topic_id)
            print(url)
            offset = 0

            while True:
                print(f"Offset: {offset}")
                params = {
                    "offset": str(offset),
                    "limit": "20"
                }
                try:
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                except (ChunkedEncodingError, ConnectionError) as e:
                    print(f"请求失败: {e}, url:{url}, params:{params}, topic_id:{topic_id}")
                    break
                except KeyboardInterrupt as e:
                    print(f"请求失败: {e}, url:{url}, params:{params}, topic_id:{topic_id}")
                    raise

                data = response.json().get('data', [])
                if not data:
                    print('找不到data')
                    break

                for item in data:
                    target = item.get('target')
                    type = target.get('type')
                    if type == 'answer':
                        question_id = target.get('question', {}).get('id')
                        question_url = f"https://www.zhihu.com/question/{question_id}"
                        question_title = target.get('question', {}).get('title')

                        if question_url not in existing_question_links:
                            question_output_file.write(question_url + ' ' + question_title + '\n')
                            question_output_file.flush()
                            existing_question_links.add(question_url)

                        answer_id = item['target']['url'].split('/')[-1]
                        answer_url = f"https://www.zhihu.com/question/{question_id}/answer/{answer_id}"
                        if answer_url not in existing_answer_links:
                            answer_output_file.write(answer_url + ' ' + question_title + '\n')
                            answer_output_file.flush()
                            existing_answer_links.add(answer_url)
                    elif type == 'article':
                        article_id = target.get('id')
                        article_url = f"https://zhuanlan.zhihu.com/p/{article_id}"
                        article_title = target.get('title')
                        if article_url in existing_article_links:
                            print(f"Article URL already exists: {article_url}")
                            continue
                        article_output_file.write(article_url + ' ' + article_title + '\n')
                        article_output_file.flush()
                        existing_article_links.add(article_url)
                    else:
                        print(f"Unknown type: {type}")
                offset += 20

if __name__ == "__main__":
    main()