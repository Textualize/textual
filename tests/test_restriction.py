from __future__ import annotations

from textual.restriction import Restrictor


class AllowedRestrictor(Restrictor):
    def allowed(self, value: str) -> bool:
        return True


class DisallowedRestrictor(Restrictor):
    def allowed(self, value: str) -> bool:
        return False


class UppercaseRestrictor(Restrictor):
    def allowed(self, value: str) -> bool:
        return value.isupper()


def test_allowed_restrictor():
    restrictor = AllowedRestrictor()
    assert restrictor.allowed("string") == True


def test_disallowed_restrictor():
    restrictor = DisallowedRestrictor()
    assert restrictor.allowed("string") == False


def test_uppercase_restrictor():
    restrictor = UppercaseRestrictor()
    assert restrictor.allowed("STRINg") == False
    assert restrictor.allowed("STRING") == True
