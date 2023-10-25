# target-sas7bdat

This is a [Singer](https://singer.io) target that reads JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

## How to use it

`target-sas7bdat` works together with any other [Singer Tap] to move data from sources to generate .sas7bdat file. 

## To get started

For Unix
```bash
› git clone https://github.com/kang20006/target-sas7bdat.git
› cd target-sas7bdat
› python3 -m venv ~/.virtualenvs/target-sas7bdat
› source ~/.virtualenvs/target-sas7bdat/bin/activate
› pip install -e .
› deactivate

```

For Window
```bash
› git clone https://github.com/kang20006/target-sas7bdat.git
› cd target-sas7bdat
› python -m venv ./virtualenvs/target-sas7bdat
› ./virtualenvs/target-sas7bdat/Scripts/activate
› pip install -e .
› deactivate

```
## Configuration for SAS

1. open 'target-sas7bdat'
2. config the 'sascfg.py'
more info https://sassoftware.github.io/saspy/configuration.html#iom

## Configure target

```json
   {
  "user": "user",
  "password": "password",
  "libname": "libname",
  "libpath":"path",
  "tablename":"tablename"
}

   ```
## Usage

 ```bash
   ~/.virtualenvs/tap-something/bin/tap-something \
     | ~/.virtualenvs/target-sas7bdat/bin/target-sas7bdat \
       --config ~/singer.io/target_sas7bdat_config.json
   ```

   If you are running windows, the following is equivalent:

   ```
   venvs\tap-something\Scripts\tap-something.exe | ^
   venvs\target-sas7bdat\Scripts\target-sas7bdat.exe ^
   --config target_sas7bdat_config.json
   ```

---

Copyright &copy; 2018 Stitch
