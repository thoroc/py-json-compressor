import binascii
import json
import zlib
import pytest

from src.json_compressor import (
    InvalidJsonFormatException,
    InvalidJsonDataException,
    UnableToUnzipException,
    InvalidJsonDecodedException,
    JsonCompressor,
)


@pytest.fixture()
def uncompressed():
    return {"a": "A", "b": "B"}


@pytest.fixture()
def compressed():
    return "eJyrVkpUslJQclTSUVBKArGclGoBLeoETw=="


@pytest.fixture()
def items(uncompressed):
    return [123, "123", uncompressed]


class TestJsonCompressor:

    def test_compress(self, compressed, uncompressed):
        # Arrange
        expected = {JsonCompressor.KEY: compressed}

        # Act
        actual = JsonCompressor.compress(uncompressed)

        # Assert
        assert expected == actual

    def test_decompress_ok(self, compressed, uncompressed):
        # Arrange
        expected = uncompressed
        data = {JsonCompressor.KEY: compressed}

        # Act
        actual = JsonCompressor.decompress(data)

        # Assert
        assert expected == actual

    def test_decompress_missing_key_insist(self, compressed):
        # Arrange
        data = {"foo": compressed}

        # Act & Assert
        with pytest.raises(InvalidJsonFormatException):
            JsonCompressor.decompress(data, insist=True)

    def test_decompress_missing_key(self, compressed):
        # Arrange
        expected = {"foo": compressed}

        # Act
        actual = JsonCompressor.decompress(expected, insist=False)

        # Assert
        assert actual == expected

    def test_decompress_base64_decode_exception(self, mocker):
        # Arrange
        mocker.patch("base64.b64decode", side_effect=binascii.Error)
        data = {JsonCompressor.KEY: b"foo"}

        # Act & Assert
        with pytest.raises(InvalidJsonDataException):
            JsonCompressor.decompress(data)

    def test_decompress_decompress_exception(self, mocker, compressed):
        # Arrange
        mocker.patch("zlib.decompress", side_effect=zlib.error)
        data = {JsonCompressor.KEY: compressed}

        # Act & Assert
        with pytest.raises(UnableToUnzipException):
            JsonCompressor.decompress(data)

    def test_decompress_json_decompress_exception(self, mocker, compressed):
        # Arrange
        mocker.patch(
            "json.loads",
            side_effect=json.JSONDecodeError("error", "", 1)
        )
        data = {JsonCompressor.KEY: compressed}

        # Act & Assert
        with pytest.raises(InvalidJsonDecodedException):
            JsonCompressor.decompress(data)
