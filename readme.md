# IBMEC: Projeto Cloud

# Alunos: 
- Pedro de Castro Kurtz: 202407278752
- Bruno Pilão da Rocha: 202201037911

docker build -t api_binance .

docker run -p 80:80 api_binance

docker tag api_binance containerbinanceapi.azurecr.io/api_binance:latest

docker push containerbinanceapi.azurecr.io/api_binance:latest

az login 