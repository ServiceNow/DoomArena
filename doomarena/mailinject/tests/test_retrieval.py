import pytest
from doomarena.mailinject.environment.assets import EMAILS_3
from doomarena.mailinject.environment.bm25 import (
    email_retrieval,
)  # Replace 'your_module' with the actual module name
from doomarena.mailinject.types import Email


def test_email_retrieval_zenith_query():
    query = "Zenith"
    results = email_retrieval(EMAILS_3, query, k=5)

    # Assert that we got up to 10 results
    assert len(results) <= 5

    # Check that all returned emails mention "Zenith"
    for email in results:
        assert "zenith" in email.content.lower()

    # Optional: check at least some known Zenith-specific emails are included
    known_zenith_senders = {
        "john.doe@tech.com",
        "sarah.lee@operations.com",
        "michael.brown@finance.com",
        "emily.clark@design.com",
        "ryan.taylor@sales.com",
    }
    returned_senders = {email.from_ for email in results}
    assert (
        known_zenith_senders & returned_senders
    )  # at least one known Zenith sender must be in results
