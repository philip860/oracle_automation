#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: philip860.oracle

short_description: Runs custom queries on an Oracle database with SSL/TLS support using python-oracledb

version_added: "1.0.0"

description: 
  - This module logs into an Oracle database securely using Oracle Wallet for SSL authentication.

options:
    username:
        description: Oracle database username.
        required: true
        type: str
    password:
        description: Oracle database password.
        required: true
        type: str
    host:
        description: Oracle database host.
        required: true
        type: str
    port:
        description: Oracle database port (default 1521).
        required: false
        type: int
        default: 1521
    service_name:
        description: Oracle database service name.
        required: true
        type: str
    use_tcps:
        description: Use TCPS (SSL/TLS) instead of TCP.
        required: false
        type: bool
        default: false
    wallet_location:
        description: Absolute path to the Oracle Wallet directory.
        required: false
        type: str
    client_lib_dir:
        description: Absolute path to the Oracle Instant Client library (containing `libclntsh.so`).
        required: false
        type: str
    action:
        description: The action to perform (e.g., 'export').
        required: true
        type: str
        choices: ['export']
    table_name:
        description: The name of the table to export.
        required: false
        type: str
    save_path:
        description: Path where the exported CSV file will be saved.
        required: false
        type: str

author:
    - philipduncan860@gmail.com
'''

EXAMPLES = r'''
- name: Export Oracle Database Table over TCPS
  philip860.oracle:
    username: "{{ oracle_username }}"
    password: "{{ oracle_password }}"
    host: "{{ oracle_host }}"
    port: 2484
    service_name: "{{ oracle_service_name }}"
    use_tcps: true
    wallet_location: "/usr/lib/oracle/21/client64/wallet"
    client_lib_dir: "/usr/lib/oracle/21/client64/lib"
    save_path: "/tmp/exported_db.csv"
    table_name: "SQA"
    action: "export"
'''

RETURN = r'''
message:
    description: A summary of the action taken.
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import oracledb
import csv
import os

def export_table_to_csv(cursor, table_name, save_path):
    """Exports a table to a CSV file."""
    try:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        
        with open(save_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(columns)
            writer.writerows(cursor.fetchall())

        return f"Table {table_name} exported successfully to {save_path}"
    except Exception as e:
        return f"Failed to export table {table_name}: {str(e)}"

def validate_wallet(wallet_location):
    """Check if the wallet directory exists and contains any files."""
    if not wallet_location or not os.path.isdir(wallet_location):
        return False, f"Wallet location '{wallet_location}' does not exist or is not a directory."

    # Ensure that at least one file exists in the wallet directory
    wallet_files = os.listdir(wallet_location)
    if not wallet_files:
        return False, f"Wallet location '{wallet_location}' is empty. No wallet files found."

    return True, ""

def run_module():
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        host=dict(type='str', required=True),
        port=dict(type='int', required=False, default=1521),
        service_name=dict(type='str', required=True),
        use_tcps=dict(type='bool', required=False, default=False),
        wallet_location=dict(type='str', required=False, default=""),
        client_lib_dir=dict(type='str', required=False, default=""),
        action=dict(type='str', required=True, choices=['export']),
        table_name=dict(type='str', required=False),
        save_path=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        message=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    username = module.params['username']
    password = module.params['password']
    host = module.params['host']
    port = module.params['port']
    service_name = module.params['service_name']
    use_tcps = module.params['use_tcps']
    wallet_location = module.params.get('wallet_location', "")
    client_lib_dir = module.params.get('client_lib_dir', "")
    action = module.params['action']
    table_name = module.params.get('table_name')
    save_path = module.params.get('save_path')

    if not host:
        module.fail_json(msg="Missing required parameter: host")

    if module.check_mode:
        module.exit_json(**result)

    try:
        # Initialize Oracle Client if Thick mode is required
        if client_lib_dir and os.path.isdir(client_lib_dir):
            oracledb.init_oracle_client(lib_dir=client_lib_dir)
            os.environ["LD_LIBRARY_PATH"] = client_lib_dir

        # Set up TCPS connection using Oracle Wallet
        if use_tcps:
            wallet_valid, wallet_msg = validate_wallet(wallet_location)
            if not wallet_valid:
                module.fail_json(msg=wallet_msg)

            os.environ["TNS_ADMIN"] = wallet_location
            os.environ["WALLET_LOCATION"] = wallet_location
            os.environ["SSL_CERT_DIR"] = wallet_location
            os.environ["IGNORE_ANO_ENCRYPTION_FOR_TCPS"] = "TRUE"

            # Construct DSN
            dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCPS)(HOST={host})(PORT={port}))(CONNECT_DATA=(SERVICE_NAME={service_name})))"

            connection = oracledb.connect(user=username, password=password, dsn=dsn)

        else:
            # Standard TCP connection
            dsn = f"{host}:{port}/{service_name}"
            connection = oracledb.connect(user=username, password=password, dsn=dsn)

        cursor = connection.cursor()

        if action == "export":
            if not table_name or not save_path:
                module.fail_json(msg="Both 'table_name' and 'save_path' are required for export action")

            message = export_table_to_csv(cursor, table_name, save_path)
            result['changed'] = True
            result['message'] = message

        cursor.close()
        connection.close()

    except oracledb.DatabaseError as e:
        error_msg = f"Database connection failed: {str(e)}"
        module.fail_json(msg=error_msg, **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
