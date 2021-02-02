Sonarqube project report
=

Generates a cvs file reflecting sonarqube's project dashboard.

Usage
-

`python report.py <filename> [<tagname>]`

Queries all projects available. Cannot report more than 50 at once (at the moment). Filter using `tagname`(s) if you have more than 50.
Generates cvs report at `filename` location - overwrites existing files.

Installation
- 

+ Install dependencies: \
`pip install -r requirements.txt`

+ Configure environment variables:\
`SONARQUBE_API_BASE` base path to api - e.g. https://sonarqube.example.com/api/ \
`SONARQUBE_API_USERTOKEN` user token used for basic authentication. See https://docs.sonarqube.org/latest/user-guide/user-token/ for details.

How to read the report
-

Every line represents a project. Columns show the project metrics using the keys used and explained here: https://docs.sonarqube.org/latest/user-guide/metric-definitions/