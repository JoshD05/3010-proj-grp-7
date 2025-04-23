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

# Configure PostgreSQL authentication
RUN sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf

# Initialize PostgreSQL and set up user
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "ALTER USER postgres WITH PASSWORD 'student';" && \
    createdb webapp_db && \
    /etc/init.d/postgresql stop

USER root

# Set Apache ServerName
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Create application directory and set permissions
RUN mkdir -p /var/www/webapp && \
    chown -R www-data:www-data /var/www/webapp

# Copy Python application files
COPY assignment/Webpages/*.py /var/www/webapp/
RUN chmod 755 /var/www/webapp/*.py && \
    chown -R www-data:www-data /var/www/webapp

# Configure Apache WSGI
RUN echo '<VirtualHost *:80>\n\
    ServerName localhost\n\
    WSGIDaemonProcess webapp user=www-data group=www-data threads=5 python-path=/var/www/webapp\n\
    WSGIScriptAlias / /var/www/webapp/wsgi.py\n\
    <Directory /var/www/webapp>\n\
        WSGIProcessGroup webapp\n\
        WSGIApplicationGroup %{GLOBAL}\n\
        Require all granted\n\
    </Directory>\n\
</VirtualHost>' > /etc/apache2/sites-available/000-default.conf

# Create WSGI entry point
RUN echo 'import sys\n\
import os\n\
sys.path.insert(0, "/var/www/webapp")\n\
from csdashboard import app as application' > /var/www/webapp/wsgi.py

COPY db_backup/db_backup.sql /tmp/

RUN echo '#!/bin/bash\n\
service postgresql start\n\
echo "PostgreSQL started"\n\
if [ -f /tmp/db_backup.sql ]; then\n\
  echo "Restoring database from backup"\n\
  su - postgres -c "psql -d webapp_db -f /tmp/db_backup.sql"\n\
fi\n\
# Configure PostgreSQL access\n\
cat > /etc/postgresql/14/main/pg_hba.conf << EOL\n\
# TYPE  DATABASE        USER            ADDRESS                 METHOD\n\
local   all            postgres                                trust\n\
local   all            all                                     trust\n\
host    all            all             127.0.0.1/32           trust\n\
host    all            all             ::1/128                trust\n\
host    all            all             0.0.0.0/0              trust\n\
EOL\n\
service postgresql restart\n\
apache2ctl -M\n\
service apache2 restart\n\
echo "Apache started"\n\
# Keep container running\n\
tail -f /dev/null' > /start.sh && \
chmod +x /start.sh

EXPOSE 80
EXPOSE 5432

CMD ["/start.sh"]
