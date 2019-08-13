FROM python:3.7-alpine

WORKDIR /app

COPY jwt_demo.py .
COPY jwt_entrypoint.sh .

RUN pip install --upgrade pip==19.2.1 && pip install pyjwt flask

EXPOSE 5000
CMD ["sh", "jwt_entrypoint.sh"]
