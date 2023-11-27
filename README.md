# GPTActionHub: A Repository of GPT actions

API hosts and GPT creators meet to create capable GPTs.

Live nonfunctional prototype at [gptactionhub.com](https://gptactionhub.com)

## For API Hosts

* API setup: Adhere to a standard API specification for seamless action integration.
* API directory
* Logs of usage

## For GPT Creators

* Action Integration: Enhance GPT models by incorporating selected marketplace actions.
* Combine actions across providers
* Stats and logs

# Development

## requirements

* Python 3.11+
* CouchDB

## CouchDB setup

To setup your development database run:
```
ADMIN_USER=[admin] ADMIN_PASSWORD=[password] python init-db.py
```

## portal server

1. `cd proxy`
2. `pip install -r requirements`
3. Start locally
```
ENCRYPTION_KEY=LnV8Yu9U-AKL64E21H2vgfYzm_ujDrrRd_9-f414Wys= GITHUB_CLIENT_ID=8522ed8241ccedda2657 GITHUB_CLIENT_SECRET=c602ea156da0546ce4caa02c96ac0e68ea2d71eb python main.py
```

## proxy

1. Start the proxy server:
```
ENCRYPTION_KEY=LnV8Yu9U-AKL64E21H2vgfYzm_ujDrrRd_9-f414Wys= python proxy.py
```
