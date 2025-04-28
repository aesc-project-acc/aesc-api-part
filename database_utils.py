import pandas as pd


from warnings import filterwarnings
filterwarnings("ignore")


def add_new_token(token):
    df = pd.read_csv('database.csv')
    new_row = pd.DataFrame([{'Token': token, 'LeftRequests': 5}])
    pd.concat([df, new_row], ignore_index=True).to_csv('database.csv', index=False)


def check_token(token):
    df = pd.read_csv('database.csv')
    return not df[df.Token == token].empty


def get_left_requests(token):
    df = pd.read_csv('database.csv')
    return df[df.Token == token]['LeftRequests'].values[0]


def decrement_left_requests(token):
    df = pd.read_csv('database.csv').drop(columns=['Unnamed: 0'], axis=1)
    idx = df[df.Token == token].index
    df['LeftRequests'][idx] -= 1
    df.to_csv('database.csv')
