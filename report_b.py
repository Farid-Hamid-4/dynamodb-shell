from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd
from report_a import *
import numpy as np
from itertools import groupby


def create_reportB(dynamodb, tokens):
    try:
        year = tokens[0]
        num_countries = get_num_countries(dynamodb, year)
        years = get_years(dynamodb, 'fhamid_economic')
        decades = get_decades(years)

        document = []
        document.append(Spacer(20, 20))
        document.append(Paragraph('<b>Report B - Global Report</b>',
                        ParagraphStyle(name='Report name', fontSize=14, alignment=TA_LEFT)))
        document.append(Spacer(0, 15))
        document.append(Paragraph("<b>Global Report</b>", ParagraphStyle(
            name='Name of Country', fontSize=14, alignment=TA_CENTER)))
        document.append(Spacer(0, 10))
        document.append(Paragraph(
            f"<b>Year: {year}</b>", ParagraphStyle(name='Year', fontSize=12, alignment=TA_LEFT)))
        document.append(Spacer(0, 5))
        document.append(Paragraph(f"<i>Number of Countries:</i> {num_countries}", ParagraphStyle(
            name='Number of Countries', fontSize=12, alignment=TA_LEFT)))
        document.append(Spacer(0, 20))
        document.append(Paragraph("<b>Table of Countries Ranked by Population</b> <i>(largest to smallest)</i>",
                        ParagraphStyle(name='Table 1 description', fontSize=12, alignment=TA_LEFT)))
        document.append(Spacer(0, 10))
        document.append(create_pop_table(dynamodb, year, num_countries))
        document.append(Spacer(0, 20))
        document.append(Paragraph("<b>Table of Countries Ranked by Area</b> <i>(largest to smallest)</i>",
                        ParagraphStyle(name='Table 2 description', fontSize=12, alignment=TA_LEFT)))
        document.append(Spacer(0, 10))
        document.append(create_area_table(dynamodb, num_countries))
        document.append(Spacer(0, 20))
        document.append(Paragraph("<b>Table of Countries Ranked by Density</b> <i>(largest to smallest)</i>",
                        ParagraphStyle(name='Table 3 description', fontSize=12, alignment=TA_LEFT)))
        document.append(Spacer(0, 10))
        document.append(create_density_table(dynamodb, year, num_countries))
        document.append(Spacer(0, 20))
        document.append(Paragraph("<b>GDP Per Capita for all Countries</b>",
                        ParagraphStyle(name="GDPPC Decades Header", fontSize=12, alignment=TA_LEFT)))
        document.append(Spacer(0, 10))
        for decade in decades:
            document.append(Paragraph(f"<b>{decade[0]}'s Table</b>", ParagraphStyle(
                name="Decade header", fontSize=12, alignment=TA_LEFT)))
            document.append(Spacer(0, 20))
            decade_data = get_decade_data(dynamodb, decade)
            table = create_decade_table(decade_data, decade)
            document.append(table)
            document.append(Spacer(0, 15))
        SimpleDocTemplate(f"pdf/{year}.pdf", pagesize=letter, rightMargin=40,
                          leftMargin=40, topMargin=40, bottomMargin=40).build(document)

    except Exception as error:
        print(f"{terminal.FAIL}Error:{error}{terminal.ENDC}")
    return

# Get the total number of countries from fhamid_people


def get_num_countries(dynamodb, year):
    response = dynamodb.Table('fhamid_people').scan(
        AttributesToGet=['Country', year])
    object = pd.DataFrame(response['Items']).to_dict("records")
    return len(object)


# Get the all the ranks for a table
def get_all_rank(dynamodb, table_name, key):
    response = dynamodb.Table(table_name).scan(
        AttributesToGet=['Country', key])
    object = pd.DataFrame(response['Items'])
    object[key] = object[key].astype(int)
    object = object.sort_values([key], ascending=False)
    return object


def create_pop_table(dynamodb, year, num_countries):
    data = []
    data.append(["Country Name", "Population", "Rank"])
    object = get_all_rank(dynamodb, 'fhamid_people', year).to_dict("records")
    for i in range(0, num_countries):
        if (object[i][year] != 'nan'):
            pop_country = object[i]['Country']
            population = object[i][year]
            rank = i+1
            data.append([pop_country, population, rank])
    table = Table(data, colWidths=[2.4*inch])
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))
    return table


def get_all_density_rank(dynamodb, year, num_countries):
    response = dynamodb.Table('fhamid_people').scan(
        AttributesToGet=['Country', year, 'Area'])
    object = pd.DataFrame(response['Items'])
    object[year] = object[year].astype(int)
    object['Area'] = object['Area'].astype(int)
    object['Density'] = object[year]/object['Area']
    object = object.sort_values(['Density'],  ascending=False)
    list = []
    for i in range(1, num_countries+1):
        list.append(i)
    object['Rank'] = list
    object.drop(year, axis=1, inplace=True)
    object.drop('Area', axis=1, inplace=True)
    return object


def create_area_table(dynamodb, num_countries):
    data = []
    data.append(["Country Name", "Area (sq km)", "Rank"])
    object = get_all_rank(dynamodb, 'fhamid_people', 'Area').to_dict("records")
    for i in range(0, num_countries):
        if (object[i]['Area'] != 'nan'):
            country = object[i]['Country']
            area = object[i]['Area']
            rank = i+1
            data.append([country, area, rank])
    table = Table(data, colWidths=[2.4*inch])
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))
    return table


def create_density_table(dynamodb, year, num_countries):
    data = []
    data.append(["Country Name", "Density (people / sq km)", "Rank"])
    object = get_all_density_rank(
        dynamodb, year, num_countries).to_dict("records")
    for i in range(0, num_countries):
        if (object[i]['Density'] != 'nan'):
            country = object[i]['Country']
            density = "{:.2f}".format(object[i]['Density'])
            rank = i+1
            data.append([country, density, rank])
    table = Table(data, colWidths=[2.4*inch])
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))
    return table


def get_decades(years):
    years = [int(i) for i in years]  # Convert the years from str to int
    # Create a list of lists that contains for the decades
    decades = np.array([list(g) for k, g in groupby(years, lambda i: i // 10)])
    return decades


def get_decade_data(dynamodb, decade):
    # Convert all items in the decade list to strings
    decade = [str(i) for i in decade]
    response = dynamodb.Table('fhamid_economic').scan()
    df = pd.DataFrame(response['Items'])
    # Keep only the Country Name and the years for the specified decade
    df = df[['Country'] + decade]
    df = df.sort_values(['Country'])
    # Convert the 'nan' values for years to -1 and cast it as a float
    df[decade] = df[decade].fillna(-1).astype(float)
    # Cast the values to int after float cast
    df[decade] = df[decade].fillna(-1).astype(int)
    return df


def create_decade_table(df, decade):
    data = []
    # First item to append will be the column header names
    data.append(list(df))
    df = df.values.tolist()  # Create a list from the df dict
    for item in df:
        temp = item[1:]
        result = all(element == -1 for element in temp)
        if (result == False):  # If all the elements are equal to -1, then don't display it as they are 'nan' values obtained from DynamoDB
            data.append(item)

    # Creates the table using the data and styles it
    table = Table(data)
    table.setStyle(TableStyle([
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10)
    ]))
    return table
