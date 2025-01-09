# Cases

### Local postgresdb container
```zsh
docker run -d \
  --name postgres-community \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=community \
  -p 5432:5432 \
  -v ~/Personal/DB/postgres-nity:/var/lib/postgresql/data \
  --user "$(id -u):$(id -g)" \
  postgres:15
```

### Local chromadb container
```zsh
docker run -d \                                                              
  --name chromadb-nity \
  -p 5433:8000 \
  -v ~/Personal/DB/chromadb-nity:/chroma/data \
  -e PERSIST_DIRECTORY=/chroma/data \
  chromadb/chroma
```
### Local rabbitmq container
```zsh
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

### Unable to install psycopg2

```text
...
pg_config is required to build psycopg2 from source.  Please add the directory
      containing pg_config to the $PATH or specify the full executable path with the
      option:

          python setup.py build_ext --pg-config /path/to/pg_config build ...

      or with the pg_config option in 'setup.cfg'.

      If you prefer to avoid building psycopg2 from source, please install the PyPI
      'psycopg2-binary' package instead.
...
```

#### Solution:

1. `brew install libpq openssl` - install pg client and openssl
2. `echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc` - export var
3. `export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib -L/opt/homebrew/opt/libpq/lib" `
4. `export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include -I/opt/homebrew/opt/libpq/include"`
5. `source ~/.zshrc` - reload terminal session
6. ARCHFLAGS="-arch arm64" pip install psycopg2-binary