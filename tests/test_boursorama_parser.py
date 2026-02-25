import hashlib
from decimal import Decimal

import pytest

from parsers.boursorama import BoursoramaCsvParser

# CSV minimal reproduisant le format Boursorama réel (multi-comptes)
SIMPLE_CSV = b"""\
"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"
"2025-01-15","2025-01-15","CARTE Amazon","Achats","Shopping",-29.99,"","ACC001","Mon Compte",1500.00,"CB","amazon"
"2025-01-16","2025-01-16","VIR Salaire","Revenus","Revenus",2500.00,"","ACC001","Mon Compte",4000.00,"","employeur"
"2025-01-17","2025-01-17","CARTE Carrefour","Alimentation","Vie quotidienne",-45.50,"","ACC002","Autre Compte",800.00,"CB","carrefour"
"""

MASKED_ACCOUNT_CSV = b"""\
"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"
"2025-03-31","2025-03-31","CARTE 28/03/25 U EXPRESS","Alimentation","Vie quotidienne",-50.72,"","4810****2680","Joint","","CB_charles","u express"
"""

EMPTY_BALANCE_CSV = b"""\
"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"
"2025-05-01","2025-05-01","VIR TEST","Divers","Divers",100.00,"","ACC003","Test","","","test merchant"
"""

NO_SUPPLIER_CSV = b"""\
"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"
"2025-06-01","2025-06-01","VIR SEPA Loyer","Logement","Logement",-800.00,"","ACC001","Mon Compte",200.00,"",""
"""


@pytest.fixture
def parser() -> BoursoramaCsvParser:
    return BoursoramaCsvParser()


class TestBoursoramaCsvParserParsing:
    def test_parse_two_accounts(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        assert len(result.accounts) == 2

    def test_account_num_and_label(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        assert acc1.account_label == "Mon Compte"

    def test_transaction_count_per_account(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        acc2 = next(a for a in result.accounts if a.account_num == "ACC002")
        assert len(acc1.transactions) == 2
        assert len(acc2.transactions) == 1

    def test_transaction_amount(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        amazon_txn = next(t for t in acc1.transactions if "Amazon" in t.description)
        assert amazon_txn.amount == Decimal("-29.99")

    def test_last_balance_per_account(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        # La dernière ligne d'ACC001 a balance 4000.00
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        assert acc1.balance == Decimal("4000.00")

    def test_empty_balance_gives_none(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(EMPTY_BALANCE_CSV)
        assert len(result.accounts) == 1
        assert result.accounts[0].balance is None

    def test_masked_account_num(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(MASKED_ACCOUNT_CSV)
        assert len(result.accounts) == 1
        assert result.accounts[0].account_num == "4810****2680"


class TestBoursoramaCsvParserMerchant:
    def test_merchant_set_when_supplier_found(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        amazon_txn = next(t for t in acc1.transactions if "Amazon" in t.description)
        assert amazon_txn.merchant is not None
        assert amazon_txn.merchant.normalized_name == "amazon"

    def test_merchant_none_when_no_supplier(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(NO_SUPPLIER_CSV)
        assert len(result.accounts[0].transactions) == 1
        assert result.accounts[0].transactions[0].merchant is None


class TestBoursoramaCsvParserImportHash:
    def test_import_hash_is_sha256(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        amazon_txn = next(t for t in acc1.transactions if "Amazon" in t.description)

        expected_hash = hashlib.sha256(b"2025-01-15|ACC001|-29.99|CARTE Amazon").hexdigest()
        assert amazon_txn.import_hash == expected_hash

    def test_import_hash_is_64_chars(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        for account in result.accounts:
            for txn in account.transactions:
                assert len(txn.import_hash) == 64

    def test_import_hashes_are_unique_within_file(self, parser: BoursoramaCsvParser) -> None:
        result = parser.parse(SIMPLE_CSV)
        all_hashes = [
            txn.import_hash for account in result.accounts for txn in account.transactions
        ]
        assert len(all_hashes) == len(set(all_hashes))


class TestBoursoramaCsvParserEncoding:
    def test_parse_latin1_encoded_csv(self, parser: BoursoramaCsvParser) -> None:
        latin1_csv = SIMPLE_CSV.decode("utf-8").encode("latin-1")
        result = parser.parse(latin1_csv)
        assert len(result.accounts) == 2

    def test_parse_utf8_bom_encoded_csv(self, parser: BoursoramaCsvParser) -> None:
        bom_csv = b"\xef\xbb\xbf" + SIMPLE_CSV
        result = parser.parse(bom_csv)
        assert len(result.accounts) == 2


class TestBoursoramaCsvParserEdgeCases:
    def test_empty_csv_returns_empty(self, parser: BoursoramaCsvParser) -> None:
        header_only = b'"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"\n'
        result = parser.parse(header_only)
        assert result.accounts == []

    def test_row_missing_amount_skipped(self, parser: BoursoramaCsvParser) -> None:
        csv_missing_amount = b"""\
"dateOp","dateVal","label","category","categoryParent","amount","comment","accountNum","accountLabel","accountbalance","CB","supplierFound"
"2025-01-01","2025-01-01","Test","","","","","ACC001","Test","","",""
"""
        result = parser.parse(csv_missing_amount)
        assert result.accounts == []

    def test_dates_parsed_correctly(self, parser: BoursoramaCsvParser) -> None:
        from datetime import date

        result = parser.parse(SIMPLE_CSV)
        acc1 = next(a for a in result.accounts if a.account_num == "ACC001")
        amazon_txn = next(t for t in acc1.transactions if "Amazon" in t.description)
        assert amazon_txn.transaction_date == date(2025, 1, 15)
        assert amazon_txn.booking_date == date(2025, 1, 15)
