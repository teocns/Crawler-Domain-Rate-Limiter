  
FROM python:3


RUN apt update -y && \
    apt install -y python3-pip && \ 
    apt install -y python3-pip



COPY . .


RUN pip3 install --no-cache-dir -r  /requirements.txt

EXPOSE 5011



CMD ["uwsgi", "--plugin" , "python" , "--ini-paste", "uwsgi.ini"]


