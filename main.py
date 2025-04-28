from fastapi import FastAPI


import database_utils
import ml
print("ready")
app = FastAPI()


admin_token = 'ctdca9v6cybsowt6u4woa25tmud8czid'


@app.get("/")
def read_root():
    return "Привет!"


@app.get("/address/{eth_wallet_address}")
def read_address(eth_wallet_address: str, api_token: str = None):
    if api_token is None:
        return "Передайте API-Token!"
    if not database_utils.check_token(api_token):
        return f"API-Token {api_token} не зарегистрирован!"
    if database_utils.get_left_requests(api_token) == 0:
        return "Вы исчерпали свой лимит на бесплатные запросы. Если вам понравился наш проект - рассмотрите приобретение подписки."

    database_utils.decrement_left_requests(api_token)
    return ml.get_predict_by_address(eth_wallet_address)


@app.get("/add_token/{new_token}")
def add_address(new_token: str, api_token: str = None):
    if api_token is None:
        return "Передайте API-Token!"
    if api_token != admin_token:
        return "API-Token не админский!"

    database_utils.add_new_token(new_token)
    return "Новый токен успешно зарегистрирован!"
