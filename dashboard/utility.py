class Data:
    """
    Utility class to handle url encryption and decryption
    """
    @classmethod
    def encode_data(cls, data):
        """
        Encodes data to generate a hash.
        This hash is used to generate urls

        :param data: The data to be encoded.
        :returns: hash value
        """
        return "%08x" % (data * 387420489 % 4000000000)

    @classmethod
    def decode_data(cls, data):
        """
        Decodes the data encoded by 'encode_data' function.

        :param data: The hash value to be decoded.
        :returns: original data
        """
        return int(data, 16) * 3513180409 % 4000000000

