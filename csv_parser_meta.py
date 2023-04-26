
class CsvParserMeta(type):
    """
        A Parser metaclass that will be used for csv parser class creation.
    """
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'process') and 
                callable(subclass.process) and
                hasattr(subclass, '_process_data') and 
                callable(subclass._process_data) and
                hasattr(subclass, '_dropNonData') and 
                callable(subclass._dropNonData) and 
                hasattr(subclass, '_get_time_column') and 
                callable(subclass._get_time_column) and
                hasattr(subclass, '_get_data') and 
                callable(subclass._get_data))

class CsvParserInterface(metaclass=CsvParserMeta):
    
    pass

