FROM python:alpine
ARG editable
ARG extras
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy just the setup.py file over
COPY setup.py README.md ./

# install any dependencies that pip needs to build and install (currently psycopg2)
# Also create an empty src directory so that pip will install ONLY the dependencies
# This allows us to cache the install step, and only execute this when setup.py changes
# Install postgresql-libs separately because its needed after installation
# you *COULD* install psycopg2 with the static-libpq build option, but I can't
# figure out how to do that
RUN apk add --no-cache postgresql-libs && \
  apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
  mkdir src && \
  pip install ${editable:+-e}.${extras:+[$extras]} && \
  apk del --no-cache .build-deps

COPY src ./src
RUN pip install --no-deps ${editable:+-e}.${extras:+[$extras]}
