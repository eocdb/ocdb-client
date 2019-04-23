# eocdb-client

EUMETSAT Ocean Colour Database (OCDB) Python Client


## Installation

```bash
git clone https://github.com/bcdev/eocdb-client
cd eocdb-client
conda env create
source activate eocdb-client-dev
python setup.py develop
```

## API Usage


## CLI Usage

__Config__:

In order to access the database you need to configure the client.
The default address is ```http://194.76.223.169```.

```bash

eocdb-cli conf server_url http://194.76.223.169

```

__Search Database__:

```bash

eocdb-cli ds find --expr "investigators: *Colleen*"

```

__Add User__:

```bash

eocdb-cli user add -u admin -p admin -fn Submit -ln Submit -em jj -ph hh -r admin

```

__Login User__:


```bash

eocdb-cli user login

```

__Delete User__:


```bash

eocdb-cli user delete

```


__Submission__:

__Delete Submission__:

__Download Submission__:

__Download Submission File__:

__Upload Submission File__:


## Development

### Testing

    $ pytest --cov=eocdb_client --cov-report html 
