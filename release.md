```shell
docker build -f Dockerfile.scheduler -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-scheduler:1.0 -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-scheduler:latest .
```

```shell
docker build -f Dockerfile.executor -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-executor:1.0 -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-executor:latest .
```

---

```shell
2025-01-18 14:12:02,260 - infrastructure.pg_repositories.engine - INFO - Database connection established: postgresql://nityadmin:nityadmin@rc1a-dua0o475iapmddcz.mdb.yandexcloud.net:6432/tasks
2025-01-18 14:12:02,330 - api.service - INFO - Loaded gRPC server reflection data for api.proto.tasks_service_pb2
2025-01-18 14:14:12,962 - infrastructure.rabbitmq.broker_client - WARNING - Failed to create vhost via HTTP API: HTTPConnectionPool(host='rabbitmq', port=15672): Max retries exceeded with url: /api/vhosts/collector (Caused by ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x7fd938f83dd0>, 'Connection to rabbitmq timed out. (connect timeout=None)'))
2025-01-18 14:14:12,963 - infrastructure.rabbitmq.broker_client - ERROR - Failed to create vhost via command: [Errno 2] No such file or directory: 'rabbitmqctl'
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 800, in get
    return self._context[key]
           ~~~~~~~~~~~~~^^^^^
KeyError: <class 'infrastructure.rabbitmq.broker_client.BrokerClient'>

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/urllib3/connection.py", line 198, in _new_conn
    sock = connection.create_connection(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/urllib3/util/connection.py", line 85, in create_connection
    raise err
  File "/usr/local/lib/python3.11/site-packages/urllib3/util/connection.py", line 73, in create_connection
    sock.connect(sa)
TimeoutError: [Errno 110] Connection timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py", line 787, in urlopen
    response = self._make_request(
               ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py", line 493, in _make_request
    conn.request(
  File "/usr/local/lib/python3.11/site-packages/urllib3/connection.py", line 445, in request
    self.endheaders()
  File "/usr/local/lib/python3.11/http/client.py", line 1298, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/local/lib/python3.11/http/client.py", line 1058, in _send_output
    self.send(msg)
  File "/usr/local/lib/python3.11/http/client.py", line 996, in send
    self.connect()
  File "/usr/local/lib/python3.11/site-packages/urllib3/connection.py", line 276, in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/urllib3/connection.py", line 207, in _new_conn
    raise ConnectTimeoutError(
urllib3.exceptions.ConnectTimeoutError: (<urllib3.connection.HTTPConnection object at 0x7fd938f83dd0>, 'Connection to rabbitmq timed out. (connect timeout=None)')

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
           ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
              ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='rabbitmq', port=15672): Max retries exceeded with url: /api/vhosts/collector (Caused by ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x7fd938f83dd0>, 'Connection to rabbitmq timed out. (connect timeout=None)'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/infrastructure/rabbitmq/broker_client.py", line 34, in _ensure_vhost_exists
    self._create_vhost_via_api()
  File "/app/infrastructure/rabbitmq/broker_client.py", line 49, in _create_vhost_via_api
    response = requests.get(
               ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/requests/adapters.py", line 688, in send
    raise ConnectTimeout(e, request=request)
requests.exceptions.ConnectTimeout: HTTPConnectionPool(host='rabbitmq', port=15672): Max retries exceeded with url: /api/vhosts/collector (Caused by ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x7fd938f83dd0>, 'Connection to rabbitmq timed out. (connect timeout=None)'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/main_executor.py", line 7, in <module>
    from services import tasks_queue
  File "/app/services/tasks_queue.py", line 18, in <module>
    broker_client = container.get(BrokerClient)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 91, in wrapper
    return function(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 976, in get
    provider_instance = scope_instance.get(interface, binding.provider)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 91, in wrapper
    return function(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 802, in get
    instance = self._get_instance(key, provider, self.injector)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 813, in _get_instance
    return provider.get(injector)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 302, in get
    return injector.call_with_injection(self._callable)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/injector/__init__.py", line 1050, in call_with_injection
    return callable(*full_args, **dependencies)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/infrastructure/di/modules.py", line 27, in provide_rabbitmq_connection
    return BrokerClient()
           ^^^^^^^^^^^^^^
  File "/app/infrastructure/rabbitmq/broker_client.py", line 25, in __init__
    self._ensure_vhost_exists()
  File "/app/infrastructure/rabbitmq/broker_client.py", line 39, in _ensure_vhost_exists
    self._create_vhost_via_command()
  File "/app/infrastructure/rabbitmq/broker_client.py", line 86, in _create_vhost_via_command
    subprocess.run(
  File "/usr/local/lib/python3.11/subprocess.py", line 548, in run
    with Popen(*popenargs, **kwargs) as process:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/subprocess.py", line 1026, in __init__
    self._execute_child(args, executable, preexec_fn, close_fds,
  File "/usr/local/lib/python3.11/subprocess.py", line 1955, in _execute_child
    raise child_exception_type(errno_num, err_msg, err_filename)
FileNotFoundError: [Errno 2] No such file or directory: 'rabbitmqctl'
```