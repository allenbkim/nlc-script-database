# Norman Lear Center Script Database
## Overview
[The Norman Lear Center](https://learcenter.org/) (NLC) is a multi-disciplinary research and public policy center exploring implications of the convergence of entertainment, commerce, and society and is based at the USC Annenberg School for Communication. One of NLC's current research projects (as of summer/fall 2019) involves analyzing the portrayal of philanthropy in TV shows and movies in the past decade. As part of this research, NLC wished to search through scripts for key words and phrases and explore the contexts in which they are used.

To aid in this research, a PostgreSQL database was created to hold script data scraped from [Springfield, Springfield](https://www.springfieldspringfield.co.uk/) using the [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) Python package. A [Django](https://www.djangoproject.com/) web site was created to perform the searches and export information as CSV files, and the database model was defined in the project. TV/Movie titles, scripts, and release year information was scraped from the web and temporarily stored as text files, then migrated to the database with the [Psycopg2](http://initd.org/psycopg/) Python package.

The final product was deployed to Amazon Web Services as an Elastic Beanstalk application using the [EB CLI](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html) utility.

## Screenshots
### Login
![Login](screenshots/login.png)
### Search Results
![Results](screenshots/search_results.png)