#!/bin/sh
set -e

export NAMESPACES=${BASE}/namespaces

if [ ! -f ${NAMESPACES}/${NAMESPACE} ]
  then
    echo "Namespace ${NAMESPACES}/${NAMESPACE} does not exist - dynamically generating..."
    #Default ergo protocol is amqp
    echo "protocol: ${ERGO_PROTOCOL}" > ${NAMESPACES}/${NAMESPACE}
    if [ -z ${ERGO_HOST} ]
      then
        echo "ERGO_HOST not set!"
        exit 1
    fi
    echo "host: ${ERGO_HOST}" >> ${NAMESPACES}/${NAMESPACE}
    #Default ergo exchange is primary
    echo "exchange: ${ERGO_EXCHANGE}" >> ${NAMESPACES}/${NAMESPACE}
fi
if [ -f ${BASE}/config/${MANIFEST} ]
  then
    echo "Using config ${BASE}/config/${MANIFEST}"
    exec ergo start "${BASE}/config/${MANIFEST}" $@
  else
    echo "Using dynamically generated config"
    MANIFEST="config.yaml"
    echo "namespace: ${NAMESPACES}/${NAMESPACE}" > ${MANIFEST}
    #ERGO_FUN should have a default set by the component
    echo "func: ${ERGO_FUNC}" >> ${MANIFEST}
    if [ -z ${ERGO_SUB} ]
      then
        echo "ERGO_SUB not set!"
        exit 1
    fi
    echo "subtopic: ${ERGO_SUB}" >> ${MANIFEST}
    if [ -z ${ERGO_PUB} ]
      then
        echo "ERGO_PUB not set!"
        exit 1
    fi
    echo "pubtopic: ${ERGO_PUB}" >> ${MANIFEST}

    exec ergo start "${MANIFEST}" $@
fi