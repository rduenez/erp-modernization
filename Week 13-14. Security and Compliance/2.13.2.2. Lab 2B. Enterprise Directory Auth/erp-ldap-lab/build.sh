mkdir erp-ldap-lab
cd erp-ldap-lab
podman network create ldap-net

# Start the OpenLDAP server
podman run --name corp-ldap --network ldap-net -e LDAP_ORGANISATION="ERP Corp" -e LDAP_DOMAIN="erp.com" -e LDAP_ADMIN_PASSWORD="SuperAdminPassword" -p 389:389 -d osixia/openldap:1.5.0

# Seed the LDAP directory with test users
podman build -t ldap-tools .
podman run --name erp-ldap-api --network ldap-net -v .:/app -p 5022:5022 --rm -d ldap-tools python ldap_api.py
