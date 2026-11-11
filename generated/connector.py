
import os
import logging
import time
from urllib.parse import urlparse

import requests

# Configuration
BASE_URL = "https://api.calendly.com"
CURRENT_USER_ENDPOINT = "/users/me"
ORG_MEMBERSHIPS_ENDPOINT = "/organization_memberships"
SCHEDULED_EVENTS_ENDPOINT = "/scheduled_events"

MAX_PAGES = 10
TIMEOUT = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger(__name__)


# API Client
class CalendlyClient:

    def __init__(self):
        token = os.getenv("CALENDLY_TOKEN")

        if not token:
            raise ValueError("CALENDLY_TOKEN environment variable is missing.")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        })

    def get(self, endpoint, params=None):

        if endpoint.startswith("https://"):
            parsed = urlparse(endpoint)

            if parsed.netloc != "api.calendly.com":
                raise ValueError("Unapproved API host.")

            url = endpoint
        else:
            url = f"{BASE_URL}{endpoint}"

        for attempt in range(4):

            response = self.session.get(
                url,
                params=params,
                timeout=TIMEOUT
            )

            if response.status_code == 429:
                wait = min(
                    int(response.headers.get("Retry-After", 2)),
                    15
                )

                if attempt == 3:
                    response.raise_for_status()

                logger.info("Rate limit reached; retrying.")
                time.sleep(wait)
                continue

            if response.status_code >= 500:
                if attempt == 3:
                    response.raise_for_status()

                time.sleep(2 ** attempt)
                continue

            response.raise_for_status()
            return response.json()

        raise Exception("Calendly request failed after retries.")


# Pagination
def fetch_all_items(client, endpoint, params=None):

    all_items = []
    next_url = endpoint
    seen_urls = set()

    for page_number in range(MAX_PAGES):

        if next_url in seen_urls:
            raise ValueError("Repeated pagination URL detected.")

        seen_urls.add(next_url)

        logger.info(
            "Fetching page %d from %s",
            page_number + 1,
            endpoint
        )

        response_data = client.get(
            next_url,
            params=params if next_url == endpoint else None
        )

        all_items.extend(response_data.get("collection", []))

        # Calendly provides a complete next_page URL.
        next_url = response_data.get(
            "pagination", {}
        ).get("next_page")

        if not next_url:
            logger.info(
                "Retrieved %d records.",
                len(all_items)
            )
            return all_items

    raise ValueError("Maximum pagination limit reached.")


# Retrieve organization users
def get_users(client, organization_uri):

    params = {
        "organization": organization_uri,
        "count": 100
    }

    memberships = fetch_all_items(
        client,
        ORG_MEMBERSHIPS_ENDPOINT,
        params
    )

    users = []

    for membership in memberships:

        user = membership.get("user", {})

        users.append({
            "external_user_id": user.get("uri"),
            "name": user.get("name"),
            "email": user.get("email"),
            "role": membership.get("role")
        })

    logger.info(
        "Successfully retrieved %d organization users.",
        len(users)
    )

    return users


# Retrieve scheduled events
def get_usage(client, organization_uri):

    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=30)

    params = {
        "organization": organization_uri,
        "min_start_time": start.isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "max_start_time": now.isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "count": 100
    }

    events = fetch_all_items(
        client,
        SCHEDULED_EVENTS_ENDPOINT,
        params
    )

    normalized_events = []

    for event in events:

        normalized_events.append({
            "event_uri": event.get("uri"),
            "name": event.get("name"),
            "status": event.get("status"),
            "start_time": event.get("start_time"),
            "end_time": event.get("end_time"),
            "created_at": event.get("created_at")
        })

    logger.info(
        "Successfully retrieved %d scheduled events.",
        len(normalized_events)
    )

    return normalized_events


# Main execution
def main(dry_run=False):

    try:

        logger.info("Starting Calendly integration.")
        
        client = CalendlyClient()

        # Authenticate and retrieve organization context
        current_user_data = client.get(
            CURRENT_USER_ENDPOINT
        )

        current_user = current_user_data.get("resource", {})
        organization_uri = current_user.get(
            "current_organization"
        )

        if not organization_uri:
            raise ValueError(
                "No organization associated with this Calendly account."
            )

        logger.info("Calendly authentication successful.")

        # Retrieve users
        logger.info("Fetching organization memberships.")

        users = get_users(
            client,
            organization_uri
        )

        # Retrieve usage
        logger.info("Fetching scheduled event activity.")

        events = get_usage(
            client,
            organization_uri
        )

        # Safe dry-run output
        if dry_run:

            print("\n===== CALENDLY SANDBOX RESULTS =====")

            print("Status: SUCCESS")
            print("Users retrieved:", len(users))
            print("Events retrieved:", len(events))
            print("Usage window: Last 30 days")

            print("\nMasked user preview:")

            for user in users[:5]:
                print({
                    "name": "REDACTED",
                    "email": "REDACTED",
                    "role": user.get("role")
                })

            print("\n====================================")

        return 0

    except requests.HTTPError as error:

        status = (
            error.response.status_code
            if error.response is not None
            else "Unknown"
        )

        logger.error(
            "Calendly API request failed. HTTP status: %s",
            status
        )

        print("SANDBOX_RESULT=FAIL")
        return 1

    except Exception as error:

        logger.error(
            "Integration failed: %s",
            type(error).__name__
        )

        print("SANDBOX_RESULT=FAIL")
        return 1


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    args = parser.parse_args()

    raise SystemExit(
        main(dry_run=args.dry_run)
    )
