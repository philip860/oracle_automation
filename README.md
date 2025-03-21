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
