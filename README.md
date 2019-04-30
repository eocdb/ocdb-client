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


## Getting Started

__Config__:

In order to access the database you need to configure the client.
The default address is ```http://194.76.223.169```.

```bash

eocdb-cli conf server_url http://194.76.223.169

```


```python

from eocdb_client.api.OCDBApi import new_api

api = new_api()

api.config

#Out[11]: {'server_url': 'http://eocdb-server:4000'}


api.server_url='http://localhost:4000'

api.config

#Out[18]: {'server_url': 'http://localhost:4000'}


```


__Search Database__:


The databse can be searched using the so-called Lucene syntax. The Lucene
syntax allows you to query specific fields and also allows to apply logic,
chaining of queries, and using wild cards.

The first example searches for instance attempts to find data files
that include the name Colleen in the investigators meta field.

```bash

eocdb-cli ds find --expr "investigators: *Colleen*"

```

```python

api.find_datasets(investigators="*Colleen*")

```


## User Management

For the user managent the command line is used even though it is possible
teh API as well.


__Login User__:


The example below will login a user with the user name scott. scott is
a dummy user that should be present in the EUMETSAT production database
 lacking any privileges.

The login procedure returns an API key that can be used for CLI or API
calls that require admin or submit privileges. The API key is user specific
and changes occasionally.

```bash

eocdb-cli user login --user scott --password tiger

```


```python

api_key = api.login_user(username='scott', password='tiger')

```

__Add User__:

To add a user, specify the required user information


```bash

eocdb-cli user add -u admin -p admin -fn Submit -ln Submit -em jj -ph hh -r admin

```

```python

api.add_user(username='<user_name>', password='<passwd>', roles=['<role1>, <role2>'])

```


__Get User__:


```bash

eocdb-cli user get --user scott --api-key <your key>

```

```python

api.get_user(name=<user_name>)

```


__Delete User__:


```bash

eocdb-cli user delete --user scott --api-key <your key>

```

```python

api.delete_user(name=<user_name>)

```


__Update User__:

```bash

eocdb-cli user update --key last_name --value <your value>

```

```python

from eocdb_client.api.OCDBApi import new_api

api = new_api()

api.update_user(name=<user_name>, key=<key>, value=<value>)

```


## Managing Submissions

__Get Submission__:


```bash

eocdb-cli sbm get --submission-id <submission-id>

```


```python

api.get_submission(<submission-id>)

```


__Get Submissions for a specific User__:


```bash

eocdb-cli sbm user --user-id <user-id>

```


```python

api.get_submissions_for_user(<user-id>)

```


__Delete Submission__:


```bash

eocdb-cli sbm delete --submission-id <submission-id>

```


```python

api.delete_submission(<submission-id>)

```


__Update Submission Status__:


```bash

eocdb-cli sbm status --submission-id <submission-id> --status <status>

```


```python

api.update_submission_status(<submission-id>, <status>)

```


__Download Submission File__:


```bash

eocdb-cli sbm download --submission-id <submission-id> --index <index>

```


```python

api.download_submission_file(<submission-id>, <index>)

```


__Upload Submission File__:


```bash

eocdb-cli sbm upl --submission-id <submission-id> --index <index> --file <file>

```


```python

api.upload_submission_file(<submission-id>, <index>, <file>)

```


## General

__Get License__


```bash

eocdb-cli lic

```


## Development

### Testing

    $ pytest --cov=eocdb_client --cov-report html
