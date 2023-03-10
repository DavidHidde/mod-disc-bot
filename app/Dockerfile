FROM python:3.11.2

WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt
RUN /bin/bash -c "apt-get update && apt-get install jq -y"
RUN /bin/bash -c "./install_cog_requirements.sh"

# Run the bot
CMD [ "python", "main.py" ]
