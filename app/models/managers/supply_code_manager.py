from django.db import models


class SupplyCodeManager(models.Manager):
    def create_supply_code(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # For set of all supply codes, each code must be unique
        while self.filter(code=code):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        supply_code = self.model(code=code)
        supply_code.save(using=self._db)
        return supply_code
