# enedisgateway2mqtt

![Version: 2.2.1](https://img.shields.io/badge/Version-2.2.1-informational?style=flat-square) ![AppVersion: 1.1.1](https://img.shields.io/badge/AppVersion-1.1.1-informational?style=flat-square)

Fully configurable Enocean to MQTT Gateway and Control Panel

**This chart is not maintained by the upstream project and any issues with the chart should be raised [here](https://github.com/k8s-at-home/charts/issues/new/choose)**

## Source Code

- https://github.com/m4dm4rtig4n/enedisgateway2mqtt
- https://hub.docker.com/r/m4dm4rtig4n/enedisgateway2mqtt

## Requirements

Kubernetes: `>=1.16.0-0`

## Dependencies

| Repository | Name | Version |
|------------|------|---------|
| https://library-charts.k8s-at-home.com | common | 4.0.1 |

## TL;DR

```console
helm upgrade --install enedisgateway2mqtt Chart/ -f values.yaml
```

## Installing the Chart

To install the chart with the release name `enedisgateway2mqtt`

```console
helm upgrade --install enedisgateway2mqtt Chart/ -f values.yaml
```

## Uninstalling the Chart

To uninstall the `enedisgateway2mqtt` deployment

```console
helm uninstall enedisgateway2mqtt
```

The command removes all the Kubernetes components associated with the chart **including persistent volumes** and deletes the release.

## Configuration

Read through the [values.yaml](Chart/values.yaml) file. It has several commented out suggested values.
Other values may be used from the [values.yaml](https://github.com/k8s-at-home/library-charts/tree/main/charts/stable/common/values.yaml) from the [common library](https://github.com/k8s-at-home/library-charts/tree/main/charts/stable/common).

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`.

```console
helm install enedisgateway2mqtt \
  --set env.TZ="America/New York" \
    m4dm4rtig4n/enedisgateway2mqtt
```

Alternatively, a YAML file that specifies the values for the above parameters can be provided while installing the chart.

```console
helm upgrade --install enedisgateway2mqtt m4dm4rtig4n/enedisgateway2mqtt -f values.yaml
```