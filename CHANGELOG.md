## CHANGES in v0.2.5:

- Fixed submission upload: It accepts now not to pass any document files 

## CHANGES in v0.2.4:

- upload_submission now accepts single files
- upload submissions accepts now None publication date and false allow_publication
- Added an API function add_submission_file
- Renamed an API function upload_submission_file to update_submission_file
- Renamed option store_path to path when uploading submissions
- Allows now to add a non validating submission file to a submission

## CHANGES in v0.2.3:

- Added api version tag to distinguish between api version and the
  tag used by the api which changed to latest during the maintenance 
  phase
- Changed api version tag to latest

## CHANGES in v0.2.2:

- A user can now add a file to a submission
- The system enforces now the file extension .zip when downloading
  submission or dataset files

## CHANGES in v0.2.1:

- The command line options are more consistent now
- Added a validation command for submission files


## CHANGES in v0.2:

- Pushed project to gitlab.eumetsat.int
- Updated URLs in README to https:ocdb.eumetsat.int
- Updated command reference eocdb-client to ocdb-client in README.md doc