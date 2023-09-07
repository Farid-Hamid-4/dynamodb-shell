# Assignment 2: DynamoDB
Name: Farid Hamid
Course: CIS 4010 - Cloud Computing
Student ID: 1067867


## REGION
`ca-central-1`


## IMPORTANT
1. May require python3, my PC and Laptop uses python version 3.10.2
2. The update_record module found in dynamodb.py is the add missing information module (4b), more on this below 
3. Exiting the program will delete the tables for you if they still exist


## How to run shell
1. Ensure that your AWS access key and secret key are in a file named `configuration.conf` (set to [default]), and is contained within the same directory as the files mentioned in step 1
3. To run the program, type <python3 main.py>


## Normal behavior of shell
1. When the program is intially run, you will be told to wait as it creates the 3 DynamoDB tables
2. The program will then create the following three csv objects to upload to DynamoDB and bulk load it with their data:
   1. fhamid_economic will use `Country` and `Years` from `shortlist_gdppc.csv` and `Currency` from `shortlist_curpop.csv`
   2. fhamid_people will use `Country` and `Years` from `shortlist_curpop.csv` and `Area` from `shortlist_area.csv`
   3. fhamid_country will `Country`, `Official Name`, `ISO3` and `ISO2` from `un_shortlist.csv`, `Captials` from `shortlist_captials.csv`, and `Languages` from `shortlist_languages.csv`
3. It will then prompt the user with options to interact with the program (modules 3a,3b,3d-3g,4b)
4. Upon exiting the program, it will delete the 3 tables from DynamoDB if they still exist


## Structure of Python Modules
   1. main.py - Creates tables, bulk loads data, allows user to manipulate the tables, and then upon exit will delete the tables (if they still exist).
      - Contains a main that runs the program and takes input through an interactive shell for modules 3a, 3b, 3d-3g, 4b

   2. dynamodb.py - Contains the the functions for 3a - 3f & 4b, along with extra helper functions
      - 3a. `create_table` module creates a table by defining the primary key as 'Country' for my 3 tables. When the user choose to create a table, `Format`: <table name><attribute name>
      - 3b. `delete_table` module deletes a table using table name. When the user choose to delete a table, `Format`: <table name>
      - 3c. `bulk_load` module loads data in bulk using a pandas dataframe and converting all the values to string before uploading. Since module 3c acts the same way as 3d, I've chosen to implement bulk load to just load data when the tables are empty, so if you'd like to bulk load data after running the progarm, then just use add_record_row.  
      - 3d. `add_record_row` module adds new row(s) of record(s) from file. Allows the user to add ONE or more rows of records into the table. Since bulk load and add individual record essentially performed the same action, I wanted to make the add_record_row the one you can interact with to add ONE or more entries into the tables. `Format`: <table name>,<file name>
      - 3d. `add_record_column` modules adds new columns from file. Allows the user to add ONE or more columns of records into the table. `Format`: <table name>,<file name>
      - 4b. `update_record` module can update a record, which acts as the missing information module. In the case of adding more languages for a country, you can pass in multiple values for Languages by seperating by commas after you name the first country. `Format`: <table name>,<Name of the Country>,<Attribute key>,<Value>
      - 3e. `delete_record` module deletes a record from a table using the primary key name, 'Country'. `Format`: <table name>,<Name of the Country>
      - 3f. `display_table` module displays the table from dynamodb by saving the data in a `display.csv` file within the csv folder for easier reading. If you try to print 'fhamid_people' to terminal, the terminal will display data in an unorganized manner because the data is longer than the terminal space. Hence why I just save it to a display.csv file to make reading easier. (Approved by Prof. Stacey on Slack). `Format`: <table name>

   3. report_a.py - Contains all the functions needed to generate a pdf report for a country, with helper functions
      - 3g. `create_reportA` function will create a pdf report for a country. `Format`: <Name of the Country>
      - All the other functions are helper functions that help to gather data and generate tables

   4. report_b.py - Contains all the functions needed to generate a pdf report for a given year, with helper functions
      - `create_reportB` function will create a pdf report for a year. `Format`: <Year>
      - All the other functions are helper functions that help to gather data and generate tables

   ### Modifications made on the csv column header names for consistency. All shorlist files are stored in the csv folder for cleanliness. These tables all have the primary key 'Country' to merge the data with.
   - For shortlist_area.csv: `ISO3,Country,Area`
   - For shortlist_capitals.csv: `ISO3,Country,Capital`
   - For shortlist_curpop.csv: `Country,Currency,1970,1971,..,2019`
   - For shortlist_gdppc.csv: `Country,1970,1971,...,2019`
   - For shortlist_languages.csv: `ISO3,Country,Languages`
   - For un_shortlist.csv: `ISO3,Country,Official Name,ISO2`


## How to use modules
3a. `create_table` Format: <table name>,<attribute name>

3b. `delete_table` Format: <table name>

3c. `bulk_load` module can only be used after the tables have been created. Users can't `bulk_load` data themselves, but they can add record(s) from file using module 3d. Since bulk load and add individual record seem to perform the same action, I thought it best that bulk_load just simply get called once by the program to load the data into the empty tables. You may use add_record_row and add_record_column to add ONE or more records to the tables.

3d. `add_record_row` and `add_record_column` module can be used add to new record(s) to the table. `Format`: <table name>,<file name> The file should contain the column header names in the order specified below:
- Column header format for fhamid_economic: `Country,1970,1971,...,2019,Currency`
- Column header format for fhamid_people: `Country,1970,1971,...,2019,Area`
- Column header format for fhamid_country: `ISO3,Country,Official Name,ISO2,Capital,Languages`
Within the files themselves, if you'd like to leave a field blank, just use a comma like in the shortlist files in the csv folder

4b. `update_record` Format: <table name>,<Name of the Country>,<Attribute key>,<Value> So just provide the table name, name of the country, the attribute key (the column header name), and the corresponding value to add. This module will update existing records based on user input, and will also serve as the module that is meant to add missing information. When adding a new language(s) to an existing record, it will simply append to whats already there. To add more than one language simply seperate the languages by commas. For example updating the languages for Canada in fhamid_country: `> fhamid_country,Canada,Languages,Spanish,Dutch`

3e. `delete_record` Format: <table name>,<Name of the Country> So provide the table name and the name of the country seperated by a comma and it will delete a record from the specified table if it exists

3f. `display_table` Format: <table name> So just provide the table name and it will create a 'display.csv' file for you with all the data in it and put it inside the csv folder. (Approved by Prof. Stacey on Slack)

## How to generate both types of reports
3g. `create_reportA` Format: <Name of the Country> So just provide the country name and it will generate a country report for it. It will save it in the pdf folder as country.pdf so you can delete all the files at once later.

`create_reportB` Format: <Year> So just provide the year and it will generate a report for that year. It will save it in the pdf folder as year.pdf so you can delete all the files at once later.


## How to edit tables
You can edit the tables through the interactive shell I've created using one of the menu options provided. Remember bulk load which is module 3c and add_record_row which is module 3d do the same thing so if you want to bulk load, just use 3d. 


## Limitations
1. All values are uploaded as strings since floats can't be proccessed by DynamoDB, they are later type casted to floats and ints when needed


## Terminal Colors Meanings: `I used terminal colors to make reading easier`
Blue - used to convey a message to the user, not meant to be interactive
White - used to notify the user that input is expected
Green - used for success messages
Red - used for error messages
