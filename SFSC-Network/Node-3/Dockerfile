FROM hyperledger/besu:latest

COPY data/ /opt/besu/data/
COPY genesis.json /opt/besu/genesis.json

EXPOSE 8547 30305

ENTRYPOINT [\
  "besu", \
  "--data-path=/opt/besu/data",\
  "--genesis-file=/opt/besu/genesis.json",\
  "--rpc-http-enabled",\
  "--rpc-http-api=ETH,NET,QBFT,WEB3",\
  "--host-allowlist=*",\
  "--rpc-http-cors-origins=*",\
  "--rpc-http-port=8547",\
  "--rpc-http-host=0.0.0.0",\
  "--p2p-port=30305",\
  "--logging=INFO",\
  "--profile=ENTERPRISE"\
]
