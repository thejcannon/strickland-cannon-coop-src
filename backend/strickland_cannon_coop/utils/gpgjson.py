import json
import pathlib

import gnupg

from strickland_cannon_coop.settings import GPG

_gpg = gnupg.GPG()
_gpg.import_keys(GPG["public_key"])
_gpg.import_keys(GPG["private_key"])


class GPGJsonFile(object):
    def __init__(self, path):
        self._path = pathlib.Path(path)

    def exists(self):
        return self._path.exists()

    def read(self):
        return json.loads(
            str(
                _gpg.decrypt(
                    self._path.read_text(),
                    passphrase=GPG["passphrase"],
                    always_trust=True,
                )
            )
        )

    def write(self, obj):
        encrypt_result = _gpg.encrypt(
            json.dumps(obj),
            recipients=GPG["recipient"],
            passphrase=GPG["passphrase"],
            always_trust=True,
        )
        if not encrypt_result.ok:
            raise ValueError(f"Failed to encrypt: {encrypt_result.status}")
        self._path.write_text(str(encrypt_result).replace("\r\n", "\n"))
