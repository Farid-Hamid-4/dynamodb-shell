import pandas as pd
import csv
from sys import exit
from report_a import get_years

# Colors for terminal messages
class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'


# Create a table in dynamodb
def create_table(dynamodb, tokens):
    try:        
        table_name = tokens[0]
        attribute_name = tokens[1]

        print(f"{bcolors.OKBLUE}Please wait, creating {table_name} can take a while...{bcolors.ENDC}", flush=True)

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': attribute_name,
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': attribute_name,
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        table.wait_until_exists()

        print(f"{bcolors.OKGREEN}{table_name} has been successfully created!{bcolors.ENDC}")

    except Exception as error:
        print(f"{bcolors.FAIL}Error: Cannot create table:\n{error}{bcolors.ENDC}")

    return


# Delete a table in dynamodb
def delete_table(dynamodb, tokens):
    try:
        table_name = tokens[0]

        print(f"{bcolors.OKBLUE}Please wait, deleting {table_name} can take a while...{bcolors.ENDC}", flush=True)

        table = dynamodb.Table(table_name)
        table.delete()
        table.wait_until_not_exists()

        print(f"{bcolors.OKGREEN}{table_name} has been successfully deleted!{bcolors.ENDC}")

    except Exception as error:
        print(f"{bcolors.FAIL}Error: Cannot delete table:\n{error}{bcolors.ENDC}")

    return


# Bulk load data from a csv file to dynamodb
def bulk_load(dynamodb, table_name, df):
    try:
        table = dynamodb.Table(table_name)
        records = df.to_dict("records")
        records = [{key: str(dict[key]) for key in dict.keys()}
                   for dict in records]  # Convert float values to string

        with table.batch_writer() as batch:
            for row in records:
                batch.put_item(Item=row)

    except Exception as error:
        print(f"{bcolors.FAIL}Error: Cannot load data in bulk:\n{error}{bcolors.ENDC}")

    return


# Add one or more records from a file into fhamid_table
def add_record_row(dynamodb, tokens):
    try:
        table = dynamodb.Table(tokens[0])

        if tokens[0] == 'fhamid_country':
            with open(tokens[1], newline='', encoding='utf8') as file:
                csv_read = csv.reader(file)
                batch_data = list(csv_read)
                start = len(batch_data[0]) - 1
                for row in batch_data:
                    with table.batch_writer() as batch:
                        batch.put_item(Item={
                            'ISO3': row[0],
                            'Country': row[1],
                            'Official Name': row[2],
                            'ISO2': row[3],
                            'Capital': row[4],
                            'Languages': ','.join(row[start:len(row)])
                        })
        else:
            pandas_object = pd.read_csv(tokens[1], dtype=object)
            records = pandas_object.to_dict("records")
            records = [{key: str(dict[key]) for key in dict.keys()}
                       for dict in records]  # Convert all values to string

            with table.batch_writer() as batch:
                for row in records:
                    batch.put_item(Item=row)

    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Cannot add record(s) - rows:\n{error}{bcolors.ENDC}")

    return


# Add one or more columns from a file into fhamid_table, merging based on primary key
def add_record_column(dynamodb, tokens):
    try:
        table = dynamodb.Table(tokens[0])

        # Create and merge pandas dataframes
        response = table.scan()
        dynamo_table = pd.DataFrame(response['Items'])
        file_table = pd.read_csv(tokens[1], dtype=object)
        dynamo_table = dynamo_table.merge(
            file_table, on=['Country'], how='outer')

        # Convert all values to strings
        records = dynamo_table.to_dict("records")
        records = [{key: str(dict[key]) for key in dict.keys()}
                   for dict in records]

        with table.batch_writer() as batch:
            for row in records:
                batch.put_item(Item=row)

    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Cannot add record(s) - columns:\n{error}{bcolors.ENDC}")

    return


# Update a record from input from a table
def update_record(dynamodb, tokens):
    try:
        table = dynamodb.Table(tokens[0])

        # Append the language to the existing languages in the dynamo table
        if (tokens[2] == 'Languages'):
            response = dynamodb.Table('fhamid_country').get_item(
                Key={
                    'Country': tokens[1]
                }
            )
            temp = response['Item']['Languages'].split(',')
            temp.append(','.join(tokens[3:]))
            tokens[3] = ','.join(temp)

        table.update_item(
            Key={
                'Country': tokens[1]
            },
            UpdateExpression='SET #colName = :value',
            ExpressionAttributeNames={
                '#colName': tokens[2]
            },
            ExpressionAttributeValues={
                ':value': tokens[3]
            }
        )
    except Exception as error:
        print(f"{bcolors.FAIL}Error: Cannot update record:\n{error}{bcolors.ENDC}")
    return


# Delete a record from input from a table
def delete_record(dynamodb, tokens):
    try:
        table = dynamodb.Table(tokens[0])
        response = table.scan()
        items = response['Items']
        for item in items:
            if (tokens[1] == item['Country']):
                table.delete_item(Key={'Country': tokens[1]})

    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Cannot delete individual record:\n{error}{bcolors.ENDC}")

    return


# Display data from a table
def display_table(dynamodb, tokens):
    try:
        table = tokens[0]
        response = dynamodb.Table(table).scan()
        df = pd.DataFrame(response['Items'])

        if (table == 'fhamid_economic'):
            years = get_years(dynamodb, table)
            years = [str(i) for i in years]
            df = df[['Country', 'Currency'] + years]
            df = df.sort_values(['Country'])

        elif (table == 'fhamid_people'):
            years = get_years(dynamodb, table)
            years = [str(i) for i in years]
            df = df[['Country', 'Area'] + years]
            df = df.sort_values(['Country'])

        elif (table == 'fhamid_country'):
            df = df.loc[:, ['Country', 'Official Name',
                            'Capital', 'Languages', 'ISO3', 'ISO2']]
            df = df.sort_values(['Country'])

        df.to_csv("csv/display.csv", index=False)

    except Exception as error:
        print(f"{bcolors.FAIL}Error: Cannot display table:\n{error}{bcolors.ENDC}")

    return


# Create a pandas DataFrame for economic data
def create_economic_df(dynamodb):
    try:  # Merge different columns of the shorlist files to create a pandas dataframe
        df_gdppc = pd.read_csv("csv/shortlist_gdppc.csv")
        df_curpop = pd.read_csv("csv/shortlist_curpop.csv")
        cols_to_use = df_curpop.columns.difference(df_gdppc.columns)
        pandas_economic = pd.merge(
            df_gdppc, df_curpop[cols_to_use], left_index=True, right_index=True, how='outer')

    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Cannot create pandas_economic DataFrame:\n{error}{bcolors.ENDC}")
        delete_table(dynamodb, 'fhamid_country')
        exit()

    return pandas_economic


# Create a pandas DataFrame for people data
def create_people_df(dynamodb):
    try:  # Merge different columns of the shorlist files to create a pandas dataframe
        df_curpop = pd.read_csv("csv/shortlist_curpop.csv")
        df_area = pd.read_csv("csv/shortlist_area.csv")
        pandas_people = df_curpop.merge(df_area, on=['Country'], how='outer')
        pandas_people.drop("Currency", axis=1, inplace=True)
        pandas_people.drop("ISO3", axis=1, inplace=True)

    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Cannot create pandas_people DataFrame:\n{error}{bcolors.ENDC}")
        delete_table(dynamodb, 'fhamid_country')
        exit()

    return pandas_people


# Create a pandas DataFrame for countries data
def create_country_df(dynamodb):
    try:  # Merge different columns of the shorlist files to create a pandas dataframe
        df_unshortlist = pd.read_csv('csv/un_shortlist.csv')
        df_capitals = pd.read_csv('csv/shortlist_capitals.csv')
        cols_to_use = df_capitals.columns.difference(df_unshortlist.columns)
        pandas_country = pd.merge(
            df_unshortlist, df_capitals[cols_to_use], left_index=True, right_index=True, how='outer')

        df_languages = pd.read_csv(
            'csv/shortlist_languages.csv', usecols=['ISO3', 'Country'])
        df_languages['Languages'] = get_languages(
            'csv/shortlist_languages.csv')
        cols_to_use = df_languages.columns.difference(pandas_country.columns)
        pandas_country = pd.merge(
            pandas_country, df_languages[cols_to_use], left_index=True, right_index=True, how='outer')

    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Cannot create pandas_country DataFramet:\n{error}{bcolors.ENDC}")
        delete_table(dynamodb, 'fhamid_country')
        exit()
    return pandas_country


def get_languages(file_name):
    try:  # Get the langauges from a specific file
        with open(file_name, newline='', encoding='utf8') as file:
            csv_read = csv.reader(file)
            batch_data = list(csv_read)
            items = []
            start = len(batch_data[0]) - 1
            for row in batch_data:
                items.append(','.join(row[start:len(row)]))
    except Exception as error:
        print(f"{bcolors.FAIL}{error}{bcolors.ENDC}")
    return items[1:]


# Check if the table exists
def table_exists(dynamodb, table_name):
    try:
        dynamodb.Table(table_name).table_status
    except:
        return False
    return True


# Upon exiting the program delete the tables
def exit_program(dynamodb, tokens):
    if (table_exists(dynamodb, 'fhamid_economic') == True): delete_table(dynamodb, ['fhamid_economic'])
    if (table_exists(dynamodb, 'fhamid_people') == True): delete_table(dynamodb, ['fhamid_people'])
    if (table_exists(dynamodb, 'fhamid_country') == True): delete_table(dynamodb, ['fhamid_country'])
    exit()
