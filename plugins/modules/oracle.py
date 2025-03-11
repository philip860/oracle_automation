#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: philip860.oracle

short_description: Runs custom queries on an Oracle database

version_added: "1.0.0"

description: 
  - This module logs into an Oracle database and performs actions such as exporting a table.

options:
    username:
        description: Oracle database username.
        required: true
        type: str
    password:
        description: Oracle database password.
        required: true
        type: str
    dsn:
        description: Oracle Data Source Name (DSN) for the database.
        required: true
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
- name: Export Oracle Database Table
  philip860.oracle:
    username: "{{ oracle_username }}"
    password: "{{ oracle_password }}"
    dsn: "{{ oracle_dsn }}"
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
import cx_Oracle
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

def run_module():
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        dsn=dict(type='str', required=True),
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
    dsn = module.params['dsn']
    action = module.params['action']
    table_name = module.params.get('table_name')
    save_path = module.params.get('save_path')

    if module.check_mode:
        module.exit_json(**result)

    try:
        connection = cx_Oracle.connect(username, password, dsn)
        cursor = connection.cursor()

        if action == "export":
            if not table_name or not save_path:
                module.fail_json(msg="Both 'table_name' and 'save_path' are required for export action")

            message = export_table_to_csv(cursor, table_name, save_path)
            result['changed'] = True
            result['message'] = message

        cursor.close()
        connection.close()

    except Exception as e:
        module.fail_json(msg=f"Database connection failed: {str(e)}", **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
