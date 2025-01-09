Generate client via

```shell
pip install "betterproto[compiler]" grpclib
```

```zsh
python -m grpc_tools.protoc -I. --python_betterproto_out=. intelligence_service.proto
```