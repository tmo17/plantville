class Nutrient:
    def __init__(self, name, type, frequency, amount):
        self.name = name
        self.type = type
        self.frequency = frequency
        self.amount = amount

    def update_field(self, field_name, value):
        if hasattr(self, field_name):
            setattr(self, field_name, value)
        else:
            raise ValueError(f"Field {field_name} not found in Nutrient.")
