
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

#
# config  httpd
#
#

# action: config

   # make directories in /etc/... and /var/... if they don't already exists
   mkdir -p /etc/httpd/conf
   mkdir -p /etc/httpd/conf.d
   mkdir -p /var/www/html
   mkdir -p /var/www/rf/static

   # copy the httpd config files
   cp ./httpd.conf /etc/httpd/conf/httpd.conf
   cp ./ssl.conf /etc/httpd/conf.d/ssl.conf

   # create the HTTPS SSL keys and certs
   # Step-0: set RMSSLCERTS to path to certs we are creating
   SSLCERTS=./sslCerts

   # Step-1: Generagte private ssl key
   #   this creates the ca.key file
   openssl genrsa -out ${SSLCERTS}/ca.key 2048

   # Step-2: Generate CSR
   #   this creates the ca.csr file from the ca.key
   openssl req -new -key ${SSLCERTS}/ca.key -out ${SSLCERTS}/ca.csr \
      -subj "/C=US/ST=TX/L=Round Rock/O=Dell Inc./OU=ESI/CN=RackManager"

   # Step-3: Generate Self Signed Key
   #   this creates the ca.crt file from the ca.csr and ca.key
   openssl x509 -req -days 365 -in ${SSLCERTS}/ca.csr -signkey ${SSLCERTS}/ca.key -out ${SSLCERTS}/ca.crt

   # copy ssl certs/keys to native location Apache uses
   #   Note: the /etc/pki/tls/certs/localhost.crt and .../private/localhost.key files
   #     are created by the post install of mod_ssl and should already be there.
   #     Otherwise, then can be created similarly
   cp ${SSLCERTS}/ca.crt   /etc/pki/tls/certs/ca.crt
   cp ${SSLCERTS}/ca.key   /etc/pki/tls/private/ca.key
   cp ${SSLCERTS}/ca.csr   /etc/pki/tls/private/ca.csr

   # set SELinux bools to allow httpd to reverse proxy to the MC or local redfish service
   echo "setting SELinux bool \"httpd_can_network_connect on\" so that it can reverse proxy"
   echo "this takes several seconds "
   # Set the bool so that the reverse proxy will work...
   #   the -P makes it persistent for future boots
   #   For some reason, this takes several seconds to execute
   setsebool -P httpd_can_network_connect on
   echo "completed setting SELinux bool.  continuing..."

   # modify the startup scripts to enable dhcp in run levels 2,3,4,5
   systemctl enable httpd.service
   systemctl restart httpd.service

   sleep 1 # as if it takes a while


