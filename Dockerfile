FROM python:3.7.6

RUN mkdir -p /init
RUN mkdir -p /logs
RUN mkdir -p /domain-messages
RUN mkdir -p /price_forecaster_state_source

# install the python libraries
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

COPY PriceForecaster.py /PriceForecaster.py
COPY init/ /init/
COPY domain-messages/ /domain-messages/
COPY price_forecaster_state_source/ /price_forecaster_state_source/

WORKDIR /

CMD [ "python3", "-u", "-m", "PriceForecaster" ]


