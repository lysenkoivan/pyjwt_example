FROM python:3.6-alpine

WORKDIR /app

COPY jwt_demo.py .
COPY jwt_entrypoint.sh .
COPY requirements.txt .

RUN pip install --upgrade pip==19.2.2 && pip install -r requirements.txt

EXPOSE 5000
CMD ["sh", "jwt_entrypoint.sh"]
