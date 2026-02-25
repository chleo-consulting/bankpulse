import io
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class ParsedMerchant:
    normalized_name: str


@dataclass
class ParsedTransaction:
    account_num: str
    transaction_date: date
    booking_date: date | None
    description: str
    amount: Decimal
    import_hash: str
    merchant: ParsedMerchant | None = None


@dataclass
class ParsedAccount:
    account_num: str
    account_label: str
    balance: Decimal | None
    transactions: list[ParsedTransaction] = field(default_factory=list)


@dataclass
class ParsedData:
    accounts: list[ParsedAccount] = field(default_factory=list)


class AbstractCsvParser(ABC):
    @abstractmethod
    def parse(self, file: bytes | io.IOBase) -> ParsedData: ...
