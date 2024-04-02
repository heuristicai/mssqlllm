
import pandas as pd
import azure_storage_helper as azhelper

df = None
def get_few_shots_df():
    success = azhelper.download_blob_to_file("fewshots","few_shots.json", "./few_shots.json")
    if not success:
        # make sure we upload the data to Azure first
        azhelper.upload_blob_file("fewshots","few_shots.json", "./data/few_shots.json")
    df = pd.read_json('few_shots.json')
    if len(df) == 0:
        df = pd.read_json('./data/few_shots.json')
    df = df.astype(str)
    return df


def update_few_shots(df):
    df = df.astype(str)
    df.to_json("./few_shots.json",orient='records')
    azhelper.upload_blob_file("fewshots","few_shots.json", "./few_shots.json")


def get_few_shots_dict():
    df = get_few_shots_df()
    dict = df.to_dict(orient='records')
    return dict
