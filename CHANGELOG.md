
# Change Log

## [0.9.5] - 2017-5-22
- This is a major upgrade to get header processing, authentication, authorization, accountService, SessionService correct compared to an implementation and to remove any "ID" hard codings in the code.
- Adds request header enforcement and generates proper response headers for the URI
- added HEAD method for all APIs that implement GET
- Account Service and SessionService
  - added password file cache so that we can add/delete users, change passwords, and authenticate against
  - supports role patch, role add, role delete
  - added account lockout processing, enable, unlock
  - added session timeout
  - added full BasicAuth, SessionAuth for multiple users,
  - added authorization - per spec and rules in 
- added JsonSchemas and Registries collections -- output now being generated
- Updated Chassis, Managers, Systems classes to construct responses based on a cache which it initializes from a Json cache file
  - so all hard coded IDs have been removed from code 
  - you can add chassis, systems, managers, fans, powerSupplies, sensors by just editing database file
- Supports interactions with a front-end reverse proxy to implement https, .
  - later will add example Apache httpd.conf and instructions/examples for creating https certs
  - by adding the reverse proxy, the simulator will support https and https and operate multi-threaded for ssl/http processing

## [0.9.2] - 2016-12-08
- fix code to work with late change in mockup data.  It was failing to load
- fixed incomplete code in systems.py modeling logs

## [0.9.1] - 2016-09-06
- Initial Public Release
- 
