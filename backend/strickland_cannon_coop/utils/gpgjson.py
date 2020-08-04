import json
import pathlib

import gnupg

from strickland_cannon_coop.settings import PASSPHRASE, RECIPIENT

_gpg = gnupg.GPG()


class GPGJsonFile(object):
    def __init__(self, path):
        self._path = pathlib.Path(path)

    def exists(self):
        return self._path.exists()

    def read(self):
        return json.loads(
            str(_gpg.decrypt(self._path.read_text(), passphrase=PASSPHRASE))
        )

    def write(self, obj):
        return self._path.write_text(
            str(
                _gpg.encrypt(
                    json.dumps(obj), recipients=RECIPIENT, passphrase=PASSPHRASE
                )
            ).replace("\r\n", "\n")
        )
