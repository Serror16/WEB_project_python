from django.db import models
from django.utils.dateformat import DateFormat

"""
The main ORM in the whole project. It is supposed to store all necessary data about taxes.
"""
class Tax(models.Model):
    # Taxable money. For example, It might be an income or a cost of a real estate
    _money: int = models.IntegerField()

    # Interest rate
    _tax_rate: int = models.PositiveSmallIntegerField()

    # Date by which a tax must be paid
    _date: DateFormat = models.DateField()

    # Countries enum
    class Country(models.TextChoices):
        RUSSIA = 'Russia',
        CHINA = 'China'

    # Country where a tax must be paid. This field defines to which mock a request will be sent
    _country: Country = models.CharField(max_length=100, choices=Country.choices)

    # Other required data for different countries
    _payload: dict = models.JSONField()

    class Meta:
        verbose_name = "Tax"
        verbose_name_plural = "Taxes"

    @property
    def money(self) -> int:
        return self._money

    @property
    def tax_rate(self) -> int:
        return self._tax_rate

    @property
    def date(self) -> DateFormat:
        return self._date

    @property
    def country(self) -> Country:
        return self._country

    @property
    def payload(self) -> dict:
        return self._payload

    @money.getter
    def tax_basement(self) -> int:
        return self._money

    @money.setter
    def money(self, money: int) -> None:
        self._money = money

    @tax_rate.getter
    def tax_rate(self) -> int:
        return self._tax_rate

    @tax_rate.setter
    def tax_rate(self, tax_rate: int) -> None:
        self._tax_rate = tax_rate

    @date.getter
    def date(self) -> DateFormat:
        return self._date

    @date.setter
    def date(self, date: DateFormat) -> None:
        self._date = date

    @country.getter
    def country(self) -> Country:
        return self._country

    @country.setter
    def country(self, country: Country) -> None:
        if country not in Tax.Country.choices:
            raise ValueError(f'Invalid country {country}')

        self._country = country

    @payload.getter
    def payload(self) -> dict:
        return self._payload

    @payload.setter
    def payload(self, payload: dict) -> None:
        self._payload = payload
