FROM hyperledger/besu:latest

COPY data/ /opt/besu/data/
COPY genesis.json /opt/besu/genesis.json

EXPOSE 30306 8548

ENTRYPOINT [ \
  "besu", \
  "--data-path=/opt/besu/data", \
  "--genesis-file=/opt/besu/genesis.json", \
  "--bootnodes=enode://591251a5043b450102c4aceba5a2fa890179b5bc08d3fb536a20b6244e9fcd8ed4d39dab2059a7eb1842a3521c477a16959f7ec0f7ff2b6eee3fae5896e6e431@172.30.0.2:30303", \
  "--rpc-http-enabled", \
  "--rpc-http-api=ETH,NET,QBFT,WEB3", \
  "--host-allowlist=*", \
  "--rpc-http-cors-origins=*", \
  "--rpc-http-port=8548", \
  "--rpc-http-host=0.0.0.0", \
  "--p2p-host=172.30.0.5",\
  "--p2p-port=30306", \
  "--logging=INFO", \
  "--profile=ENTERPRISE" \
]
