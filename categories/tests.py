class Person:
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

person = Person("Alice")
person.set_name("Bob")
name = person.get_name()
print(name) # Output: Bob
