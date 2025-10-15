import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

ROOT_DIR = os.getenv("ROOT_DIR")
print("ROOT_DIR", ROOT_DIR) 


def merge_project_data(ROOT_DIR, filename):
    """Function for preprocessing project data to Data ready for RAG"""
    try:
        # Load the data

        project_df = pd.read_csv(os.path.join(ROOT_DIR, 'data','project.csv')) 
        project_address_df = pd.read_csv(os.path.join(ROOT_DIR,'data','ProjectAddress.csv'))
        project_config_df = pd.read_csv(os.path.join(ROOT_DIR,'data','ProjectConfiguration.csv'))
        project_config_variant_df = pd.read_csv(os.path.join(ROOT_DIR,'data','ProjectConfigurationVariant.csv')) 


        # print("project_df\n", project_df.columns)
        project_df['City'] = project_df['slug'].str.extract(r'-([^-]+)-[^-]+$')[0].str.capitalize()

        project_df=project_df [['id', 'projectType', 'projectName',	'projectCategory', 'slug', 'City', 'status']] 
                            
        # Merge the dataframes
        merged_df = pd.merge(project_df, project_address_df, how="left", left_on="id", right_on="projectId")

        print(merged_df.columns)
        print(merged_df.head())

        # Debugging step
        # merged_df.to_csv("temp_dir/merged.csv", index=False)

        merged_df = pd.merge(merged_df, project_config_df, on="projectId", how='left')
        # merged_df.to_csv("temp_dir/merged_2.csv", index=False)


        project_config_variant_df = project_config_variant_df[['bathrooms','balcony', 'furnishedType', 
                                                            'lift','listingType', 'carpetArea', 'price', "configurationId"]]

        merged_df = pd.merge(merged_df, project_config_variant_df, left_on='id', right_on='configurationId', how='left')

        merged_df = merged_df[["configurationId", "propertyCategory", 'projectName','slug', 'City', 'status',
                            'landmark', 'fullAddress', 'pincode', 'type', 'bathrooms','balcony',
                                'furnishedType', 'lift', 'listingType', 'carpetArea', 'price' ]]
        # # Debugging step
        # merged_df.to_csv("temp_dir/merged_3.csv", index=False)


        merged_df.rename(columns={'type': 'BHK', 'status':'Possession Status'}, inplace=True)

        # Data Cleaning and Preparation
        merged_df['price'] = pd.to_numeric(merged_df['price'], errors='coerce') / 10000000  # Convert to Crore
        merged_df.dropna(subset=['price'], inplace=True)
        merged_df['BHK'] = merged_df['BHK'].str.extract('(\d+)').astype(float)
        merged_df.dropna(subset=['BHK'], inplace=True)

        # # Debugging step
        # merged_df.to_csv("temp_dir/merged_4.csv", index=False)

        # Create a descriptive text column for embedding
        merged_df['description'] = merged_df.apply(
            lambda row: f" Project name: {row['projectName']} is a {row['BHK']} BHK property in  city {row['City']} Property Address : {row['slug']} - {row['fullAddress']}. "
                        f" The price is {row['price']:.2f} Cr and the carpet area is {row['carpetArea']} sq. ft. "
                        f" The project is currently {row['Possession Status']}. ",
            axis=1
        ) 

        merged_df.to_csv(os.path.join(ROOT_DIR, 'data', filename), index=False)
        print(f"Ingestion file saved to {filename}") 

    except Exception as e:
        print(f"Error in merge_project_data -- {e} ")


if __name__ == '__main__':

    filename = 'ingestionData.csv'
    merge_project_data(ROOT_DIR=ROOT_DIR, filename=filename)

