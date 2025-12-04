from pysyncobj import SyncObj, SyncObjConf, replicated

class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs):
        conf = SyncObjConf()
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, conf)
        self.__data = {}

    @replicated
    def put(self, key, value):
        print("put key: ", key, " with value: ", value)
        #TODO: implement the Put operation, that sets the value of the key to be the provided value.
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise TypeError("Value must be a list of strings")
        
        self.__data[key] = value


    @replicated        
    def append(self, key, value):
        print("append key: ", key, " with value: ", value)
        #TODO: implement the Append operation, that adds the provided value to the value of the key.
        if not isinstance(key, str):
            raise TypeError("Key must be a string")
        if not isinstance(value, str):
            raise TypeError("Value must be a string")

        if key not in self.__data:
            self.__data[key] = [value]
        else:
            self.__data[key].append(value)


    def get(self, key):
        print("get key: ", key)
        #TODO: implement the Get operation, that retrieves the value of the provided key.
        if key in self.__data:
            return self.__data[key]
        else:
            print("Key not found.")
            return None

    def get_dumpfile(self):
        return self.dumpFile
