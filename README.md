# applications.security.isecl.isecl-vmw

Pre-Reqs:
python3, python3.8 virtual environment
OS: RHEL 8.4, Ubuntu 20.04

1) DB Setup:
run postgres script install_pgdb.sh in scripus folder
2) Create DB: ./create_db.sh <db name> <db user> <db password> in scripts folder

PRE-REQ
copy scs cacert from master node to /etc/scs_cert.pem

To install TCS-Client run the following command
1) populate tcs_client.env and place in home directory
2) run ./scripts/install.sh

To Check status:
	tcs-client status
	tcs-client stop
	tcs-client start

To run the unit tests run the following commands
pip install tox
tox .
