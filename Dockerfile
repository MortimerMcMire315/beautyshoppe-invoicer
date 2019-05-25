# This file is part of nexudus-usaepay-gateway.

# nexudus-usaepay-gateway is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# nexudus-usaepay-gateway is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with nexudus-usaepay-gateway.  If not, see
# <https://www.gnu.org/licenses/>.

FROM python:3.6

EXPOSE 5000

WORKDIR /nexudus-usaepay-gateway

COPY requirements.txt /nexudus-usaepay-gateway
RUN pip install -r requirements.txt

COPY main.py /nexudus-usaepay-gateway
COPY entrypoint.sh /nexudus-usaepay-gateway

COPY ./src /nexudus-usaepay-gateway/src

# For some reason ENTRYPOINT ignores errors during 'docker-compose build' and
# preserves them during 'docker-compose up', where RUN freaks out if we get
# errors during build. We have to expect errors during build, because the
# Python app can't connect to the DB until after the build, so it tries to run
# and freaks out. I've RTFM but I can't figure out why this is the behavior.
# -SAY
ENTRYPOINT bash ./entrypoint.sh python main.py
