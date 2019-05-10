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

COPY entrypoint.sh /nexudus-usaepay-gateway
#COPY alembic.ini /nexudus-usaepay-gateway
#COPY ./alembic /nexudus-usaepay-gateway/alembic
COPY main.py /nexudus-usaepay-gateway

COPY ./src /nexudus-usaepay-gateway/src

ENTRYPOINT sh ./entrypoint.sh python main.py
