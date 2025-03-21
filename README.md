# philip860.oracle — Ansible Oracle Module with SSL/TLS Support

This custom Ansible module allows secure `db_action` with Oracle databases using the `python-oracledb` library. It supports connecting via **TCPS (SSL/TLS)** using **Oracle Wallet**, and is ideal for environments requiring encrypted Oracle access.

---

## ✅ Current Features

- Secure connection using Oracle Wallet and TCPS  
- Standard TCP connection support  
- Export full Oracle table data to a clean CSV file (no quotes, escaping, or CHAR padding)

---

## 🔧 Requirements

- Oracle Instant Client (with `libclntsh.so`)
- `oracledb` Python package (test sucessfully with `Version 1.2.2` Latest `Version 3.0.0` may return "Certificate validation failure, for some Connections!"  )
- Oracle Wallet (for TCPS connections)

---

## 📦 Installation

You can install this module directly from Ansible Galaxy:

```bash
ansible-galaxy collection install philip860.oracle
```

---

## ▶️ Usage Example

```yaml
- name: Export Oracle Table Over Secure TCPS
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Export Oracle Table to CSV
      philip860.oracle.tools:
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
        db_action: "export"
```

---

## 🧪 Parameters

| Parameter         | Description                                      | Required | Type | Default |
|------------------|--------------------------------------------------|----------|------|---------|
| `username`        | Oracle DB username                               | ✅       | str  | —       |
| `password`        | Oracle DB password                               | ✅       | str  | —       |
| `host`            | Oracle DB host                                   | ✅       | str  | —       |
| `port`            | Oracle DB port                                   | ✅       | int  | 1521    |
| `service_name`    | Oracle service name                              | ✅       | str  | —       |
| `use_tcps`        | Use SSL/TLS (TCPS) with Oracle Wallet            | ❌       | bool | false   |
| `wallet_location` | Path to Oracle Wallet for secure connections     | ❌       | str  | ""      |
| `client_lib_dir`  | Path to Oracle Instant Client libraries          | ✅       | str  | ""      |
| `db_action`       | Action to perform (export currently supported)   | ✅       | str  | —       |
| `table_name`      | Name of table to export (required for `export`)  | ✅       | str  | —       |
| `save_path`       | Path to save CSV file (required for `export`)    | ✅       | str  | —       |

---

## 🛠️ Usage in Ansible Automation Platform (AAP) / AWX

To run `philip860.oracle` within **AAP or AWX**, and leverage the capabilities of the module with your environment's Oracle-wallet, you'll need to create a **custom Execution Environment** (EE) with all the necessary dependencies (like Oracle Instant Client and `oracledb`). Here's how:

### 🧱 Step 1: Create a `requirements.yml` 

Not all these collections are required except for philip860.oracle, but I like to have additional features available in my EE's.

```yaml
collections:
- awx.awx
- ansible.posix
- community.general
- community.crypto
- community.network
- community.mysql
- philip860.oracle
 
```

### 🐍 Step 2: Create a `/working_dir/requirements.txt` File 

```txt
ldap3
pyyaml
pandas
cryptography
setuptools_rust
```


###  Step 3: Download Oracle RPMs 

Navigate to URL https://www.oracle.com/database/technologies/instant-client/downloads.html
Download the oracle-instantclient-sqlplus & oracle-instantclient-basic packages for your system

```bash
#Navigate to URL https://www.oracle.com/database/technologies/instant-client/downloads.html
mkdir -p /working_dir/files
cp -r oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm /working_dir/files
cp -r oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm /working_dir/files
```


###  Step 4: Create a bash-script `/working_dir/files/oracle-client-install.sh` File

```txt
#!/bin/bash
set -e

dnf install -y libnsl2 glibc libaio libgcc libstdc++

rpm -ivh /tmp/oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm /tmp/oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm

echo "Oracle Instant Client installed."

```


### 🐳 Step 4: Create an `/working_dir/execution-environment.yml` File

```yaml
---
version: 3

build_arg_defaults:
  ANSIBLE_GALAXY_CLI_COLLECTION_OPTS: '--pre'

dependencies:
  ansible_core:
    package_pip: ansible-core==2.14.4
  ansible_runner:
    package_pip: ansible-runner
  galaxy: requirements.yml
  python:
    - six
    - psutil
  system: bindep.txt

images:
  base_image:
    name: docker.io/redhat/ubi9:latest

additional_build_files:
  - src: files/oracle-client-install.sh
    dest: configs/oracle-client-install.sh
  - src: files/wallet
    dest: configs/wallet/
  - src: files/admin
    dest: configs/admin/
  - src: files/oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm
    dest: configs/oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm
  - src: files/oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm
    dest: configs/oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm

additional_build_steps:

  prepend_base: |
    RUN /usr/bin/dnf install git -y
    RUN /usr/bin/dnf install python3-devel -y
    RUN /usr/bin/dnf install mysql -y
    RUN /usr/bin/dnf install libnsl2 -y
    RUN /usr/bin/dnf install libaio -y

  prepend_final:

     - 'RUN ls -lah /usr/local/bin/ && ls -lah /_build/configs/oracle-client-install.sh || echo "Oracle Install script missing!"'
     - 'RUN if [ -d /usr/local/bin/oracle-client-install.sh ]; then rm -rf /usr/local/bin/oracle-client-install.sh; fi'
     - 'RUN if [ -d /tmp/oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm ]; then rm -rf /tmp/oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm; fi'
     - 'RUN if [ -d /tmp/oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm ]; then rm -rf /tmp/oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm; fi'
     - 'COPY --chmod=755 --chown=root:root _build/configs/oracle-instantclient-sqlplus-21.12.0.0.0-1.el9.x86_64.rpm /tmp/'
     - 'COPY --chmod=755 --chown=root:root _build/configs/oracle-instantclient-basic-21.12.0.0.0-1.el9.x86_64.rpm /tmp/'
     - 'COPY --chmod=755 --chown=root:root _build/configs/oracle-client-install.sh /usr/local/bin/'
     - 'RUN chmod +x /usr/local/bin/oracle-client-install.sh'

     # ✅ Register with Satellite / Subscription Manager (if needed)
     - 'RUN /usr/bin/subscription-manager register --username=<your-rhn-username> --password=<your-password>'
     - 'RUN /usr/bin/subscription-manager refresh'
     - 'RUN /usr/bin/dnf repolist'
  
     # ✅ Install system dependencies
     - 'RUN dnf install mysql-devel -y'

     # ✅ Upgrade pip tools
     - 'RUN python3 -m pip install --upgrade pip setuptools wheel'

     - 'RUN pip install oracledb==1.2.2'
  
     # ✅ Run the Oracle install script
     - 'RUN /usr/local/bin/oracle-client-install.sh'
 
     # ✅ Copy Oracle wallet and admin files
     - 'RUN mkdir -p /usr/lib/oracle/21/client64/lib/network/'
     - 'RUN mkdir -p /usr/lib/oracle/21/client64/wallet/'
     - 'COPY _build/configs/wallet /usr/lib/oracle/21/client64/wallet/'
     - 'COPY _build/configs/admin /usr/lib/oracle/21/client64/lib/network/admin'
  
     - 'RUN whoami'
     - 'RUN cat /etc/os-release'
```


### 🛳️ Step 4: Build and Push the EE Container

```bash
cd /working_dir/
podman build -t quay.io/youruser/oracle-ee:latest .
podman push quay.io/youruser/oracle-ee:latest
```

### 🧰 Step 5: Register the Execution Environment in AAP/AWX

1. Go to **Execution Environments** in the AAP/AWX UI.
2. Add a new EE pointing to your image (e.g. `quay.io/youruser/oracle-ee:latest`).
3. Use this EE in your Job Templates to take full advantage of `philip860.oracle`.

---

## 🚧 Coming Soon

The following capabilities are planned for upcoming versions:

- `create_db` — Provision new Oracle databases  
- `create_table` — Create new tables dynamically  
- `insert` — Insert row data into specified tables  
- `delete` — Remove specific records from Oracle tables  
- `query` — Run ad-hoc queries and return the results to Ansible  



## AWX Job Usage

### 1. Start Oracle Export Job In AWX Server
![Start Job](https://raw.githubusercontent.com/philip860/oracle_automation/main/screenshots/AWX-Usage.PNG)

### 2. Oracle Export Job Finsihed In AWX Server
![Initial variable prompts](https://raw.githubusercontent.com/philip860/oracle_automation/main/screenshots/successfully_completed_job.PNG)






---

## 👨‍💻 Author

**philipduncan860@gmail.com**  
Licensed under **GPLv3**
