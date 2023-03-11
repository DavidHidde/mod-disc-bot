FROM python:3.11.2

WORKDIR /usr/src

COPY ./cogs.json ./cogs.json
COPY ./install_cog_requirements.sh ./install_cog_requirements.sh
COPY ./cogs ./cogs
COPY ./app ./app

RUN pip install -r app/requirements.txt
RUN /bin/bash -c "apt-get update && apt-get install jq -y"
RUN /bin/bash -c "./install_cog_requirements.sh"

# Remove bind-mounted files that are only needed for build
RUN rm -r ./cogs.json
RUN rm -r ./cogs
RUN rm ./install_cog_requirements.sh

WORKDIR /usr/src/app

# Run the bot
CMD [ "python", "main.py" ]
