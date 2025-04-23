FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    apache2 \
    python3 \
    python3-pip \
    libapache2-mod-wsgi-py3 \
    sudo \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install flask psycopg2-binary

USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER webuser1 WITH SUPERUSER PASSWORD 'password';" && \
    createdb -O webuser1 webapp_db && \
    /etc/init.d/postgresql stop

USER root

RUN sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf && \
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/14/main/pg_hba.conf

# Create application directory
RUN mkdir -p /var/www/webapp

# Copy Python application files
COPY assignment/Webpages/*.py /var/www/webapp/

# Create WSGI configuration
RUN echo 'WSGIDaemonProcess webapp python-path=/var/www/webapp\n\
WSGIProcessGroup webapp\n\
WSGIApplicationGroup %{GLOBAL}\n\
WSGIScriptAlias / /var/www/webapp/wsgi.py' > /etc/apache2/conf-available/wsgi.conf

RUN a2enconf wsgi

# Create WSGI entry point
RUN echo 'import sys\n\
sys.path.insert(0, "/var/www/webapp")\n\
from csdashboard import app as application' > /var/www/webapp/wsgi.py

COPY db_backup/db_backup.sql /tmp/

RUN echo '#!/bin/bash\n\
service postgresql start\n\
echo "PostgreSQL started"\n\
if [ -f /tmp/db_backup.sql ]; then\n\
  echo "Restoring database from backup"\n\
  su - postgres -c "psql -U webuser1 -d webapp_db -f /tmp/db_backup.sql"\n\
fi\n\
service apache2 start\n\
echo "Apache started"\n\
# Keep container running\n\
tail -f /dev/null' > /start.sh && \
chmod +x /start.sh

EXPOSE 80
EXPOSE 5432

CMD ["/start.sh"]
