```shell
docker build -f Dockerfile.scheduler -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-scheduler:1.0 -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-scheduler:latest .
```

```shell
docker build -f Dockerfile.executor -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-executor:1.0 -t cr.yandex/$N_YC_REGISTRY_ID/nity-tasks-executor:latest .
```