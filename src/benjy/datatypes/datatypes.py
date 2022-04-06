
class BaseDataType:
    aggregates_on = False


class Integer(BaseDataType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Float(BaseDataType):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Timestamp(BaseDataType):
    def __init__(self, **kwargs):
        self.frequency = kwargs.pop('frequency', None)
        self.aggregates_on = self.frequency is not None

        super().__init__(**kwargs)


def get_data_type(datatype, **kwargs):
    type_names = {
        'integer': Integer,
        'float': Float,
        'timestamp': Timestamp,
    }

    return type_names[datatype](**kwargs)

