import json
import pathlib

import gnupg

from strickland_cannon_coop.settings import GPG

_gpg = gnupg.GPG()
gpg.import_keys(GPG["public_key"])
gpg.import_keys(GPG["private_key"])


class GPGJsonFile(object):
    def __init__(self, path):
        self._path = pathlib.Path(path)

    def exists(self):
        return self._path.exists()

    def read(self):
        return json.loads(
            str(_gpg.decrypt(self._path.read_text(), passphrase=GPG["passphrase"]))
        )

    def write(self, obj):
        self._path.write_text(
            str(
                _gpg.encrypt(
                    json.dumps(obj),
                    recipients=GPG["recipient"],
                    passphrase=GPG["passphrase"],
                )
            ).replace("\r\n", "\n")
        )
