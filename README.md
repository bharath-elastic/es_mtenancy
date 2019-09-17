# es_mtenancy
Tool to create a multi-tenancy setup for training and workshops based on a csv that has spaces, roles and users to be created and assigned. Users will be assigned corresponding roles and roles will have acccess to corresponding spaces in the csv rows. Spaces here are only used for setting up multitenancy purposes and hence all features will be enabled.

## Installation
Script requires requests library and pyyam library. Install using `pip install -r requirements.txt`

## Usage
1. Before you run the script, create a role that you want to use as `role_model` for privileges on resources.
2. Modify `prov.csv` file that has the structure shown below. Alternatively create your own `csv` file using your favorite spreadsheet and use the `-p` flag to point to it.
```
user_name,space_name,role_name,role_model,pwd
analyst-01,analyst-01,analyst-01,analyst,Same4Every1
analyst-02,analyst-02,analyst-02,analyst,Same4Every1
...
```

3. Configure `config.yaml` file with cluster and login information. Alternatively copy the file and modify to create your own configuration file and use the `-c` flag when running the script. User below should have the privilege to `manage_security`. Don't provide password in yaml, script will ask you for password when run.

```
url:
  kibana: http://localhost:5601
  es: http://localhost:9200
auth:
  user: admin
```

4. Run `python3 es_m10anacy.py`. Without any flags script will default to making the setup, `config.yaml` for configuration and `prov.csv` for provisioning information. `-c` and `-p` flags can be used to override default config file and provisioning file. `--tear-down` flag will tear down the setup using the same information in provision csv so be sure to use the same file you used to setup.