from .python import PythonDriver


def get_driver(driver_id):
    drivers = {"python": PythonDriver}
    return drivers.get(driver_id)
