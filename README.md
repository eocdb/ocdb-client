# eocdb-client

EUMETSAT Ocean Colour Database (OCDB) Python Client

## Notes 

* TBD: Names
  * `path` --> `collection` (= `{affil}/{project}/{cruise}`)
  * in `find_datasets`: `offset` --> `index`, so we can have both options `--index`, `-i` in CLI
* dataset identification can either be done by id or by path plus name. 
* a dataset name may be a path, e.g. a valid name may be `chl/chl-s170604w.sub`.
* the separator character used in dataset paths and names must be a forward slash (`/`) 
  as used on Unix OS and in URLs, *not* a backslash as used on Windows OS.
* TBD: Retrieval of documentation files also done in association with datasets?
* TBD: API functions that receive entire datasets should be flexible what concerns the type of dataset 
  parameter: str = file path, dict = JSON datasets, else file handle to read from. We may miss a format 
  indication to separate SB and JSON files.
* TBD: validate_dataset() and add_dataset() ops must accept SB format in request bodies 
* TBC: the upload_store_files() CLI is currently very clumpsy. We must provide multiple 
  "-d" options to pass multiple doc files. 

## API Usage


## CLI Usage



## Development

### Testing

    $ pytest --cov=eocdb_client --cov-report html 
