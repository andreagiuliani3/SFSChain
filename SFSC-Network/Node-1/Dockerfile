FROM hyperledger/besu:latest

COPY data/ /opt/besu/data/
COPY genesis.json /opt/besu/genesis.json

EXPOSE 30303 8545

ENTRYPOINT [ \
  "besu", \
  "--data-path=/opt/besu/data", \
  "--genesis-file=/opt/besu/genesis.json", \
  "--rpc-http-enabled", \
  "--rpc-http-api=ETH,NET,QBFT,WEB3", \
  "--host-allowlist=*", \
  "--rpc-http-cors-origins=*", \
  "--rpc-http-port=8545", \
  "--rpc-http-host=0.0.0.0", \ 
  "--p2p-host=172.30.0.2",\
  "--p2p-port=30303", \
  "--logging=INFO", \
  "--profile=ENTERPRISE" \
]
