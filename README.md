# philip860.oracle — Ansible Oracle Module with SSL/TLS Support

This custom Ansible module allows secure interaction with Oracle databases using the `python-oracledb` library. It supports connecting via **TCPS (SSL/TLS)** using **Oracle Wallet**, and is ideal for environments requiring encrypted Oracle access.

### ✅ Current Features
- Secure connection using Oracle Wallet and TCPS
- Standard TCP connection support
- Export full Oracle table data to a clean CSV file (no quotes, escaping, or CHAR padding)

---

## 🔧 Requirements

- Oracle Instant Client (with `libclntsh.so`)
- `python-oracledb` Python package
- Oracle Wallet (for TCPS connections)

---

## 📦 Installation

You can install this module directly from Ansible Galaxy:

```bash
ansible-galaxy collection install philip860.oracle


## ▶️ Usage Example

```yaml
- name: Export Oracle Table Over Secure TCPS
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Export Oracle Table to CSV
      philip860.oracle:
        username: "{{ oracle_username }}"
        password: "{{ oracle_password }}"
        host: "{{ oracle_host }}"
        port: 2484
        service_name: "{{ oracle_service_name }}"
        use_tcps: true
        wallet_location: "/usr/lib/oracle/21/client64/wallet"
        client_lib_dir: "/usr/lib/oracle/21/client64/lib"
        table_name: "SQA"
        save_path: "/tmp/exported_sqa.csv"
        action: "export"


🧪 Parameters
Parameter	Description	Required	Type	Default
username	Oracle DB username	✅	str	—
password	Oracle DB password	✅	str	—
host	Oracle DB host	✅	str	—
port	Oracle DB port	❌	int	1521
service_name	Oracle service name	✅	str	—
use_tcps	Use SSL/TLS (TCPS) with Oracle Wallet	❌	bool	false
wallet_location	Path to Oracle Wallet for secure connections	❌	str	""
client_lib_dir	Path to Oracle Instant Client libraries	❌	str	""
action	Action to perform (export currently supported)	✅	str	—
table_name	Name of table to export (required for export)	❌	str	—
save_path	Path to save CSV file (required for export)	❌	str	—



🚧 Coming Soon

The following capabilities are planned for upcoming versions:

    create_db — Provision new Oracle databases
    create_table — Create new tables dynamically
    insert — Insert row data into specified tables
    delete — Remove specific records from Oracle tables
    query — Run ad-hoc queries and return the results to Ansible

Stay tuned for more database automation power in future releases!
👨‍💻 Author

philipduncan860@gmail.com
Licensed under GPLv3