"""
Base factories for the project.
"""

from factory import (  # noqa: F401
    Dict,
    Faker,
    Iterator,
    LazyAttribute,
    LazyAttributeSequence,
    LazyFunction,
    List,
    RelatedFactory,
    Sequence,
    SubFactory,
    Trait,
    lazy_attribute,
    sequence,
)
from factory.django import DjangoModelFactory as ModelFactory  # noqa: F401
from factory.fuzzy import (  # noqa: F401
    FuzzyChoice,
    FuzzyDate,
    FuzzyDateTime,
    FuzzyDecimal,
    FuzzyFloat,
    FuzzyInteger,
    FuzzyText,
)


class FuzzyBoolean(FuzzyChoice):
    """
    Factory for a Fuzzy Boolean field.
    """

    def __init__(self):
        """
        Initialize a FuzzyBoolean.
        """
        super().__init__(choices=[True, False])
