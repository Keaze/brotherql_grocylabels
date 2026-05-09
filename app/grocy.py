from dataclasses import dataclass

@dataclass
class GrocyRequest:
    raw: dict

    @property
    def product(self) -> str:
        return self.raw.get('product', '')

    @property
    def grocycode(self) -> str:
        return self.raw.get('grocycode', '')

    @property
    def details(self) -> dict:
        return self.raw.get('details', {})

    @property
    def stock_entry(self) -> dict | None:
        return self.raw.get('stock_entry')

    @property
    def due_date(self) -> str:
        if self.stock_entry:
            return self.stock_entry.get('best_before_date', '')
        return ''

    @property
    def purchase_date(self) -> str:
        if self.stock_entry:
            return self.stock_entry.get('purchased_date', '')
        return ''

    @staticmethod
    def from_json(data: dict) -> 'GrocyRequest':
        return GrocyRequest(raw=data)
