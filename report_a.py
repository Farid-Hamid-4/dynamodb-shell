from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd


class terminal:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'


def create_reportA(dynamodb, tokens):
    try:
        country = tokens[0]
        official_name = dynamodb.Table("fhamid_country").get_item(
            Key={"Country": country})["Item"]["Official Name"]
        currency = dynamodb.Table("fhamid_economic").get_item(
            Key={"Country": country})["Item"]["Currency"]

        document = []
        document.append(Spacer(20, 20))
        document.append(Paragraph("<b>Report A - Country Level Report</b>",
                        ParagraphStyle(name="Report name", fontSize=14, alignment=TA_LEFT)))
        document.append(Spacer(0, 20))
        document.append(Paragraph(f"<b>{country}</b>", ParagraphStyle(
            name="Name of Country", fontSize=14, alignment=TA_CENTER),))
        document.append(Spacer(0, 10))
        document.append(Paragraph(f"[Official Name: {official_name}]", ParagraphStyle(
            name="Official name", fontsize=14, alignment=TA_CENTER)))
        document.append(Spacer(0, 15))
        document.append(create_area_table(dynamodb, country))
        document.append(Spacer(0, 15))
        document.append(Paragraph("<b>Population</b>", ParagraphStyle(
            name="Population header", fontSize=14, alignment=TA_LEFT)))
        document.append(Spacer(0, 15))
        document.append(Paragraph("<i>Table of Population, Population Density, and their respective world ranking for that year, ordered by year:</i>",
                        ParagraphStyle(name="Population description", fontSize=11, alignment=TA_LEFT)))
        document.append(Spacer(0, 15))
        document.append(create_population_table(dynamodb, country))
        document.append(Spacer(0, 20))
        document.append(Paragraph("<b>Economics</b>", ParagraphStyle(
            name="Economic header", fontSize=14, alignment=TA_LEFT)))
        document.append(Spacer(0, 15))
        document.append(Paragraph(f"Currency: {currency}", ParagraphStyle(
            name="Population description", fontSize=11, alignment=TA_LEFT)))
        document.append(Spacer(0, 25))
        document.append(Paragraph("<i>Table of GDP per capita (GDPCC) <from earliest year to latest year> and rank within the world for that year</i>",
                        ParagraphStyle(name="Economic description", fontSize=11, alignment=TA_LEFT)))
        document.append(Spacer(0, 15))
        document.append(create_economy_table(dynamodb, country))
        document.append(Spacer(0, 15))

        SimpleDocTemplate(f"pdf/{country}.pdf", pagesize=letter, rightMargin=40,
                          leftMargin=40, topMargin=40, bottomMargin=40,).build(document)

    except Exception as error:
        print(f"{terminal.FAIL}Error:{error}{terminal.ENDC}")
    return


# Get the rank of the Country with respect to key
def get_rank(dynamodb, table_name, key, country):
    response = dynamodb.Table(table_name).scan(
        AttributesToGet=["Country", key])
    object = pd.DataFrame(response["Items"])
    object[key] = object[key].astype(float)
    object = object.sort_values([key], ascending=False)
    object.reset_index()
    counter = 0
    for idx in object.index:
        counter += 1
        if object["Country"][idx] == country:
            return counter


def create_area_table(dynamodb, country):
    area = dynamodb.Table("fhamid_people").get_item(
        Key={"Country": country})["Item"]["Area"]
    rank = get_rank(dynamodb, "fhamid_people", "Area", country)
    languages = dynamodb.Table("fhamid_country").get_item(
        Key={"Country": country})["Item"]["Languages"]
    capital = dynamodb.Table("fhamid_country").get_item(
        Key={"Country": country})["Item"]["Capital"]

    data = [[f"Area: {area} sq km (World rank: {rank})"], [
        f"Official/National Languages: {languages}\nCapital City: {capital}"],]
    table = Table(data)
    table.setStyle(
        TableStyle([
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 10)]
        )
    )
    return table


def get_population(dynamodb, country):
    response = dynamodb.Table("fhamid_people").get_item(
        Key={"Country": country})
    df = pd.DataFrame.from_dict(response["Item"], orient="index")
    return df.to_dict()[0]


def get_years(dynamodb, table_name):
    table = dynamodb.Table(table_name)
    response = table.scan()
    df = pd.DataFrame(response['Items'])
    years = list(df)
    if (table_name == 'fhamid_economic'):
        years.remove('Country')
        years.remove('Currency')
    elif (table_name == 'fhamid_people'):
        years.remove('Country')
        years.remove('Area')
    years = [int(i) for i in years]
    years.sort()
    years = [str(i) for i in years]
    return years


def create_population_table(dynamodb, country):
    area = dynamodb.Table("fhamid_people").get_item(Key={"Country": country})["Item"][
        "Area"
    ]
    data = []
    data.append(
        ["Year", "Population", "Rank",
            "Population Density\n(people/sq km)", "Rank"]
    )
    years = get_years(dynamodb, 'fhamid_people')
    population = get_population(dynamodb, country)
    for year in years:
        if population[year] != "nan":
            population_year = int(float(population[year]))
            rank = get_rank(dynamodb, "fhamid_people", year, country)
            density = "{:.2f}".format(
                float((float(population[year])) / float(area)))
            density_rank = get_density_rank(dynamodb, country, year)
            data.append([year, population_year, rank, density, density_rank])
    table = Table(data, colWidths=[1.44 * inch])
    table.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def get_density_rank(dynamodb, country, year):
    response = dynamodb.Table("fhamid_people").scan(
        AttributesToGet=["Country", year, "Area"]
    )
    object = pd.DataFrame(response["Items"]).to_dict("records")
    dict = {}
    for item in object:
        dict[item["Country"]] = float(
            (float(item[year])) / (float(item["Area"])))
    dict = {
        k: v for k, v in sorted(dict.items(), key=lambda item: item[1], reverse=True)
    }
    rank = list(dict).index(country) + 1
    return rank


def get_gdppc(dynamodb, country):
    response = dynamodb.Table("fhamid_economic").get_item(
        Key={"Country": country})
    df = pd.DataFrame.from_dict(response["Item"], orient="index")
    return df.to_dict()[0]


def create_economy_table(dynamodb, country):
    data = []
    data.append(["Year", "GDPPC", "Rank"])
    years = get_years(dynamodb, 'fhamid_economic')
    eco = get_gdppc(dynamodb, country)
    for year in years:
        if eco[year] != "nan":
            gdppc = int(float(eco[year]))
            rank = get_rank(dynamodb, "fhamid_economic", year, country)
            data.append([year, gdppc, rank])
    table = Table(data, colWidths=[2.4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table
