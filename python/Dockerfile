FROM python:3.10-alpine


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN addgroup -S mercari && adduser -S trainee -G mercari
#RUN chown -R trainee:mercari ../db

USER trainee


CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "9000"]       

