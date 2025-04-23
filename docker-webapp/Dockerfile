FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    apache2 \
    python3 \
    python3-pip \
    libapache2-mod-python \
    sudo \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install psycopg2-binary

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
RUN mkdir -p /var/www/html/cgi-bin && \
    chown -R www-data:www-data /var/www/html

# Enable CGI module
RUN a2enmod cgi

# Configure Apache for CGI
RUN echo '<VirtualHost *:80>\n\
    ServerName localhost\n\
    DocumentRoot /var/www/html\n\
    ScriptAlias /cgi-bin/ /var/www/html/cgi-bin/\n\
    <Directory "/var/www/html/cgi-bin">\n\
        AllowOverride None\n\
        Options +ExecCGI\n\
        Require all granted\n\
    </Directory>\n\
</VirtualHost>' > /etc/apache2/sites-available/000-default.conf

# Copy Python application files
COPY assignment/Webpages/*.py /var/www/html/cgi-bin/
RUN chmod 755 /var/www/html/cgi-bin/*.py && \
    chown -R www-data:www-data /var/www/html/cgi-bin

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
service apache2 restart\n\
echo "Apache started"\n\
# Keep container running\n\
tail -f /dev/null' > /start.sh && \
chmod +x /start.sh

EXPOSE 80
EXPOSE 5432

CMD ["/start.sh"]
