FROM python:3-alpine

ENV port 8343
ENV selections name2=url1&name2=url2&...


RUN cd /etc
RUN mkdir app
WORKDIR /etc/app
ADD *.py /etc/app/
ADD requirements.txt /etc/app/.
RUN pip install -r requirements.txt

CMD python /etc/app/selection_webthing.py $port $selections



