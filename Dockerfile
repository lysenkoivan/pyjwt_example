FROM python:3.6-alpine

WORKDIR /app

COPY jwt_demo.py .
COPY jwt_entrypoint.sh .
COPY requirements.txt .
RUN sed -i 's/\r//' jwt_demo.py
RUN sed -i 's/\r//' jwt_entrypoint.sh

RUN pip install --upgrade pip==19.2.2 && pip install -r requirements.txt

CMD ["sh", "jwt_entrypoint.sh"]
