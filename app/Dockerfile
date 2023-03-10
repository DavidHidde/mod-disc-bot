FROM python:3.11.2

WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt

# Run the bot
CMD [ "python", "main.py" ]
