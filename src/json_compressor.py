import zlib
import json
import base64
import binascii
from typing import Dict

from loguru import logger


class JsonCompressor:
    KEY = "base64(zip(obj))"

    @staticmethod
    def compress(data: Dict[str, str]) -> Dict[str, str]:
        """Compress a json

        Args:
            data (dict): the original json object

        Returns:
            dict: a dictionary of key JsonCompressor.KEY and value compressed/zipped data
        """
        encoded_data = json.dumps(data, sort_keys=True).encode("utf-8")
        compressed_data = zlib.compress(encoded_data)
        base64_data = base64.b64encode(compressed_data).decode('ascii')

        return {JsonCompressor.KEY: base64_data}

    @staticmethod
    def decompress(data: Dict[str, str], insist: bool = True) -> Dict[str, str]:
        """Decompress a json

        Args:
            data (dict): a dictionary of key JsonCompressor.KEY and value compressed/zipped data

        Raises:
            RuntimeError: Wrong file format
            zlib.error/binascii.Error: Decoding/Unzipping error
            json.JSONDecodeError: Cannot load data back as a dict

        Returns:
            dict: the original (decoded) json data
        """
        try:
            compressed_data = data[JsonCompressor.KEY]
        except KeyError as e:
            if insist:
                raise InvalidJsonFormatException(error=e)
            else:
                return data

        try:
            decoded_data = base64.b64decode(compressed_data, validate=True)
            logger.debug("Data Decoded")
        except binascii.Error as e:
            raise InvalidJsonDataException(error=e) from e

        try:
            decompressed_data = zlib.decompress(decoded_data)
            logger.debug("Data decompressed")
        except zlib.error as e:
            raise UnableToUnzipException(error=e) from e

        try:
            return json.loads(decompressed_data)
        except json.JSONDecodeError as e:
            raise InvalidJsonDecodedException(error=e) from e


class InvalidJsonFormatException(Exception):
    """Returns an Exception for a bad input json."""

    message = "JSON not in the expected format {{{JsonCompressor.KEY}: zipstring}}"

    def __init__(self, error):
        self.error = error


class InvalidJsonDataException(Exception):
    """Returns an Exception for bad value on the input json."""

    message = "Could not decode the contents"

    def __init__(self, error):
        self.error = error


class UnableToUnzipException(Exception):
    """Returns an Exception for failing to unzip."""

    message = "Could not unzip the contents"

    def __init__(self, error):
        self.error = error


class InvalidJsonDecodedException(Exception):
    """Returns an Exception for failing to decode the json."""

    message = "Could interpret the unzipped contents"

    def __init__(self, error):
        self.error = error
