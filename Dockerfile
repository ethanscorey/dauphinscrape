FROM python:3.11

WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install poetry
COPY pyproject.toml poetry.lock /usr/src/app/
RUN apt-get update \
&& apt-get -y install libpq-dev gcc \
&& poetry config virtualenvs.create false \
&& poetry install --no-ansi --no-interaction \
&& useradd -m scrapy
COPY . /usr/src/app/
USER scrapy
CMD ["poetry", "run", "scrapy", "crawl", "jail"]
