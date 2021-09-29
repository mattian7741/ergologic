import pytest
import pika
import json
import docker
import time
import timeout_decorator
import subprocess
from contextlib import contextmanager
from test.integration.utils import ergo
from src.topic import PubTopic, SubTopic


AMQP_HOST = "amqp://guest:guest@localhost:5672/%2F"


@pytest.fixture(scope="session")
def rabbitmq():
    """
    Start a rabbitmq server if none is running, and then wait for the broker to finish booting.
    """
    try:
        # Try running rabbitmq-server from the host system path. If this succeeds, we are presumably running
        # inside an ergo docker container.
        start_rabbitmq_baremetal()
    except FileNotFoundError:
        # Else assume we're running in a baremetal dev environment. Start rabbitmq in its own docker container.
        start_rabbitmq_container()


def start_rabbitmq_baremetal():
    subprocess.Popen(["rabbitmq-server"])

    print("awaiting broker")
    output = ""
    for retry in range(100):
        result = subprocess.run(["rabbitmqctl", "await_online_nodes", "1"])
        if result.returncode == 0:
            break
        time.sleep(.2)
    else:
        raise RuntimeError(output)
    print("broker started")


def start_rabbitmq_container():
    container_start = subprocess.run(["docker-compose", "up", "-d", "rabbitmq"])
    assert container_start.returncode == 0

    docker_client = docker.from_env()
    container, = docker_client.containers.list(filters={"name": "rabbitmq"})

    print("awaiting broker")
    output = ""
    for retry in range(200):
        try:
            exit_code, output = container.exec_run(["rabbitmqctl", "await_online_nodes", "1"])
            if exit_code == 0:
                break
        except docker.errors.APIError:
            pass
        time.sleep(.5)
    else:
        raise RuntimeError(output)
    print("broker started")


def product(x, y):
    return float(x) * float(y)


def test_product_amqp(rabbitmq):
    manifest = {
        "func": f"{__file__}:product",
    }
    namespace = {
        "protocol": "amqp",
        "host": AMQP_HOST,
        "exchange": "test_exchange",
        "subtopic": "product.in",
        "pubtopic": "product.out",
    }
    with ergo("start", manifest=manifest, namespace=namespace):
        result = rpc(json.dumps({"data": {"x": 4, "y": 5}}), **manifest, **namespace)
        assert result == 20.0


@timeout_decorator.timeout(seconds=2)
def rpc(payload, **config):
    ret = {}

    connection = pika.BlockingConnection(pika.URLParameters(config["host"]))
    for retry in _retries(20, 0.5, pika.exceptions.ChannelClosedByBroker, pika.exceptions.ChannelWrongStateError):
        with retry():
            channel = connection.channel()
            channel.exchange_declare(config["exchange"], passive=True)

    def on_pubtopic_message(body):
        result = body["data"]
        ret["result"] = result

    def on_error_mesage(body):
        error = body["error"]
        ret["error"] = error

    def add_consumer(queue_name, consumer):
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=config["exchange"], queue=queue_name)
        channel.queue_purge(queue_name)

        def on_message_callback(chan, method, properties, body):
            channel.stop_consuming()
            body = json.loads(body)
            return consumer(body)

        channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback)

    add_consumer(str(PubTopic(config["pubtopic"])), on_pubtopic_message)
    add_consumer(f"{config['func']}_error", on_error_mesage)

    # The ergo consumer may still be booting, so we have to retry publishing the message until it lands outside
    # of the dead letter queue.
    channel.confirm_delivery()
    for retry in _retries(10, 0.5, pika.exceptions.UnroutableError):
        with retry():
            channel.basic_publish(exchange=config["exchange"], routing_key=str(SubTopic(config["subtopic"])),
                                  body=payload, mandatory=True)  # noqa

    try:
        channel.start_consuming()
    finally:
        channel.close()
        connection.close()

    if ret.get("error"):
        raise Exception(ret["error"])
    return ret["result"]


def _retries(n: int, backoff_seconds: float, *retry_errors: BaseException):
    retry_errors = retry_errors or (Exception,)

    success = set()
    for attempt in range(n):
        if success:
            break

        @contextmanager
        def retry():
            try:
                yield
                success.add(True)
            except retry_errors:
                if attempt+1 == n:
                    raise
                time.sleep(backoff_seconds)

        yield retry
