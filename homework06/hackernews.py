from bottle import (
    route, run, template, request, redirect
)

from homework06.bayes import NaiveBayesClassifier
from homework06.db import News, session
from homework06.scraputils import get_news


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template.tpl', rows=rows)


@route("/add_label/")
def add_label():
    s = session()
    label = request.GET['label']
    newid = request.GET['id']
    headline = s.query(News).filter(News.id == int(newid)).all()[0]
    headline.label = label
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    news_list = get_news("https://news.ycombinator.com/newest", n_pages=1)
    cnt = 0
    for elem in news_list:
        s = session()
        if len(s.query(News).filter(News.title == elem['title']).filter(News.author == elem['author']).all()) > 0:
            print('Not writing')
            continue
        cnt += 1
        print('Writing data element:', cnt)
        news = News(title=elem['title'],
                    author=elem['author'],
                    url=elem['url'],
                    comments=elem['comments'],
                    points=elem['points'])
        s.add(news)
        s.commit()
    redirect("/news")


@route("/classify")
def classify_news():
    # 1. Получить список неразмеченных новостей из БД
    # 2. Получить прогнозы для каждой новости
    # 3. Вывести ранжированную таблицу с новостями
    s = session()

    good, maybe, never, X_train, y_train = [], [], [], [], []

    headlines_classified = s.query(News).filter(News.label != None)
    headlines_nonclassified = s.query(News).filter(News.label == None)

    for topic in headlines_classified:
        X_train.append(topic.title)
        y_train.append(topic.label)
        if topic.label == 'good':
            good.append(topic)
        elif topic.label == 'maybe':
            maybe.append(topic)
        else:
            never.append(topic)

    model = NaiveBayesClassifier()
    model.fit(X_train, y_train)

    for topic in headlines_nonclassified:
        topic.label = model.predict(topic.title)
        if topic.label == 'good':
            good.append(topic)
        elif topic.label == 'maybe':
            maybe.append(topic)
        else:
            never.append(topic)

    rows = good + maybe + never

    return template('news_template.tpl', rows=rows)


if __name__ == "__main__":
    run(host="localhost", port=8080)
