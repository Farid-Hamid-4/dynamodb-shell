from sys import exit
import boto3
# import readline # Enables arrow key functionality
import configparser
from dynamodb import *
from report_a import *
from report_b import *


# Program Information
__author__ = "Farid Hamid"
__email__ = "fhamid@uoguelph.ca"
__student_id__ = "1067867"


def shell_command(dynamodb, index):
    # Use a function dictionary to call desired functions
    if index in function_dict:
        if index != '10':
            tokens = input('> ').split(',')
        else:
            # Pass nothing for exit_program since it won't be used anyways
            tokens = ['']
        function_dict[index](dynamodb, tokens)
    else:
        print(f"{bcolors.FAIL}Error: Invalid menu option{bcolors.ENDC}")
    return


def print_menu():
    print(f"{bcolors.OKBLUE}1.  Create table: <table name>,<attribute name>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}2.  Delete table: <table name>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}3.  Add record(s) row: <table name>,<file name>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}4.  Add record(s) column: <table name>,<file name>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}5.  Update record: <table name>,<Name of the Country>,<Attribute key>,<Value>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}6.  Delete record: <table name>,<Name of the Country>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}7.  Display table: <table name>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}8.  Create Report A: <Name of the Country>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}9.  Create Report B: <Year>{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}10. Exit program{bcolors.ENDC}")
    return


function_dict = {
    '1': create_table,
    '2': delete_table,
    '3': add_record_row,
    '4': add_record_column,
    '5': update_record,
    '6': delete_record,
    '7': display_table,
    '8': create_reportA,
    '9': create_reportB,
    '10': exit_program
}


def main():
    try:  # Authenticate user for DynamoDB
        config = configparser.ConfigParser()
        config.read("configuration.conf")
        access_key = config['default']['aws_access_key_id']
        secret_key = config['default']['aws_secret_access_key']
        session = boto3.Session(region_name='ca-central-1',
                                aws_access_key_id=access_key, 
                                aws_secret_access_key=secret_key)
        dynamodb = session.resource('dynamodb', region_name='ca-central-1')
    except Exception as error:
        print(
            f"{bcolors.FAIL}Error: Could not authenticate user:\n{error}{bcolors.ENDC}")
        exit()

    try:  # Create the table, create csv objects using pandas, bulk load data into dynamo tables
        if (table_exists(dynamodb, 'fhamid_economic') == False):  # If table does not exist, create it
            create_table(dynamodb, ['fhamid_economic', 'Country'])
            pandas_economic = create_economic_df(dynamodb)
            bulk_load(dynamodb, 'fhamid_economic', pandas_economic)

        if (table_exists(dynamodb, 'fhamid_people') == False):  # If table does not exist, create it
            create_table(dynamodb, ['fhamid_people', 'Country'])
            pandas_people = create_people_df(dynamodb)
            bulk_load(dynamodb, 'fhamid_people', pandas_people)

        if (table_exists(dynamodb, 'fhamid_country') == False):  # If table does not exist, create it
            create_table(dynamodb, ['fhamid_country', 'Country'])
            pandas_country = create_country_df(dynamodb)
            bulk_load(dynamodb, 'fhamid_country', pandas_country)

    except Exception as error:
        print(f"{bcolors.FAIL}Error: Problem in main\n{error}{bcolors.ENDC}")

    while (True):
        print_menu()
        shell_command(dynamodb, input('Select a menu option by index: '))


if __name__ == "__main__":
    main()
