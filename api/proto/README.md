Generate client via

```shell
pip install "betterproto[compiler]" grpclib mypy-protobuf grpcio-tools
```

```zsh
python -m grpc_tools.protoc -I./ --python_out=. --python_betterproto_out=. --mypy_out=. tasks_service.proto
```