import datetime
from time import sleep

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import pymorphy2
import requests
from gensim.corpora import Dictionary
from gensim.models import LdaModel

ACCESS_TOKEN = ''
V = '5.103'
DOMAIN = "https://api.vk.com/method/"


def get_friends(user_id, fields):
    """ Returns a list of user IDs or detailed information about a user's friends """
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert isinstance(fields, str), "fields must be string"
    assert user_id > 0, "user_id must be positive integer"
    domain = DOMAIN + 'friends.get'
    jsn = get(domain, {'access_token': ACCESS_TOKEN, 'v': V, 'user_id': user_id, 'fields': fields}).json()
    try:
        return jsn['response']['items']
    except:
        return []


def age_predict(user_id):
    assert isinstance(user_id, int), "user_id must be positive integer"
    assert user_id > 0, "user_id must be positive integer"
    sum = 0
    cnt = 0
    friends = get_friends(user_id, 'bdate')
    for friend in friends:
        try:
            date = friend['bdate']
            if len(date) > 5:
                sum += datetime.datetime.now().year - int(friend['bdate'].split('.')[-1])
                cnt += 1
        except:
            pass
    return sum / cnt


def get_network(user_id, usernamerod):
    """ Building a friend graph for an arbitrary list of users """
    # Создание вершин и ребер

    g = nx.Graph()
    me = get(DOMAIN + 'users.get', {'access_token': ACCESS_TOKEN, 'v': V, 'user_ids': user_id}).json()['response'][0]
    my_name, my_surname = me['first_name'], me['last_name']

    friends = get_friends(user_id, 'sex')
    my_fr = set([uid['id'] for uid in friends])
    vertices = set()
    data = dict()
    colors = dict()
    for friend in friends:
        id = friend['id']
        name = friend['first_name']
        surname = friend['last_name']
        friends_list = set([uid for uid in get_friends(id, '')]).intersection(my_fr)
        for edge in friends_list:
            if (edge, id) not in vertices:
                vertices.add((edge, id))
                g.add_edge(*(edge, id))
        if (user_id, id) not in vertices:
            vertices.add((user_id, id))
            g.add_edge(*(user_id, id))
            data.update({id: name + ' ' + surname})
            colors.update({id: 'pink' if not (friend['sex'] - 1) else 'blue'})
    colors = [colors[n] if n != user_id else 'red' for n in g.nodes()]
    data.update({user_id: my_name + ' ' + my_surname})
    pos = nx.circular_layout(g, scale=0.01)
    nx.draw_networkx_nodes(g, pos, node_size=2, node_color=colors)
    nx.draw_networkx_edges(g, pos, width=0.2, edge_color='grey')
    nx.draw_networkx_labels(g, pos, font_size=2, labels=data)

    plt.title("Друзья %s во Вконтакте" % (usernamerod))
    plt.axis('off')
    plt.savefig('output.png', dpi=1500)
    return True


def get_wall(
        owner_id: str = '',
        domain: str = '',
        offset: int = 0,
        count: int = 10,
        filter: str = 'owner',
        extended: int = 0,
        fields: str = ''
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    """
    code = """return API.wall.get({
    "owner_id": "%s",
        "domain": "%s",
        "offset": "%s",
        "count": "%s",
        "filter": "%s",
        "extended": "%s",
        "fields": "%s",
        "v": "%s"
    });""" % (owner_id, domain, str(offset), str(count), filter, str(extended), fields, V)
    response = requests.post(
        url="https://api.vk.com/method/execute",
        data={
            "code": code,
            "access_token": ACCESS_TOKEN,
            "v": V
        }
    )
    return response.json()['response']['items']


def get(url, params={}, timeout=5, max_retries=5, backoff_factor=0.3):
    """ Выполнить GET-запрос

    :param url: адрес, на который необходимо выполнить запрос
    :param params: параметры запроса
    :param timeout: максимальное время ожидания ответа от сервера
    :param max_retries: максимальное число повторных запросов
    :param backoff_factor: коэффициент экспоненциального нарастания задержки
    """
    query = url + '?' + '&'.join([i + '=' + str(params[i]) for i in params.keys()])

    delay = 0.35
    cnt = -1
    while cnt < max_retries:
        try:
            response = requests.get(query)
        except:
            pass
        if response:
            return response
        sleep(delay)
        cnt += 1
        delay = min(delay * 5, timeout)
        delay += delay * backoff_factor
    return False


if __name__ == "__main__":
    morph = pymorphy2.MorphAnalyzer()
    user_id = 0
    dmn = "itmoru"
    cnt = 15

    me_rod = \
    get(DOMAIN + 'users.get', {'access_token': ACCESS_TOKEN, 'v': V, 'user_ids': user_id, 'name_case': 'gen'}).json()[
        'response'][0]

    usernamerod = me_rod['first_name'] + ' ' + me_rod['last_name']

    get_network(user_id, usernamerod)
    print("Граф друзей %s сохранен в файл output.png" % (usernamerod))

    print("Средний возраст друзей %s равен" % (usernamerod), age_predict(user_id), "лет.")

    wall = get_wall(
        owner_id="",
        domain=dmn,
        offset=0,
        count=cnt,
        filter="owner",
        extended=0,
        fields="")
    data = []
    for post in wall:
        morphed_post = []
        for word in post['text'].split():
            word = morph.parse(str(word))
            max_scr = 0
            best_morph = ''
            for prs in word:
                if prs.score >= max_scr:
                    max_scr = prs.score
                    best_morph = prs.normal_form
            c_word = "".join([letter for letter in best_morph if letter in set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')])
            if c_word:
                morphed_post.append(c_word)
        data.append(morphed_post)
    common_dictionary = Dictionary(data)
    common_corpus = [common_dictionary.doc2bow(text) for text in data]
    lda = LdaModel(common_corpus, num_topics=15)
    print("Модель последних %d записей сообщества %s успешно составлена." % (cnt, dmn))
