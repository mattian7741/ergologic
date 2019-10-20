import datetime
import os

from colors import color

from src.flask_http_invoker import FlaskHttpInvoker
from src.function_invocable import FunctionInvocable
from src.payload import Payload
from src.version import get_version


def format_date(sec: float) -> str:
    dtf: str = '%b %d %Y, %H:%M:%S.%f'
    return datetime.datetime.fromtimestamp(sec).strftime(dtf)[:-3]


def get_version_path() -> str:
    return os.path.dirname(os.path.abspath(__file__)) + '/version.py'


class ErgoCli:
    @property
    def prompt(self) -> str:
        return f'{color("ergo", fg="#33ff33")} {color("∴", fg="#33ff33")} '

    @property
    def intro(self) -> str:
        version: str = get_version()
        timestamp: str = format_date(os.path.getmtime(get_version_path()))
        intro: str = f'ergo {version} ({timestamp})\nType help or ? to list commands.'

        return str(color(intro, fg='#ffffff'))

    def run(self, ref: str, *args: str) -> bool:
        try:
            result: Payload = Payload()
            host = FunctionInvocable(ref)
            host.invoke(result, Payload(dict(zip([str(i) for i in range(len(args))], args))))
            print(str(result))
        except Exception as err:
            print(f'*** {err}')
            raise err
        return False

    def http(self, ref: str, *args: str) -> bool:
        host = FlaskHttpInvoker(FunctionInvocable(ref))
        host.start()
        return False
