from scraputils import get_news
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


Base.metadata.create_all(bind=engine)

news_list = get_news("https://news.ycombinator.com/newest", n_pages=1)
cnt = 0
for elem in news_list:
    cnt += 1
    print('Writing data element:', cnt)
    s = session(bind=engine)
    news = News(title=elem['title'],
                author=elem['author'],
                url=elem['url'],
                comments=elem['comments'],
                points=elem['points'])
    s.add(news)
    s.commit()
