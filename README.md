# TrackerAssist

TrackerAsisst is a Python library for interacting with Request Tracker's REST API 2.0 (pre-installed as of RT 5.0.0).

## Usage

```python
from TrackerAssist.tracker_assist import RTClient

# Instantiate your client
rt_client = RTClient('127.0.0.1:8000', 'secret_token', verify_cert=False)

# Get the details for a single ticket
ticket = rt_client.get_ticket(9882)

# Update an existing ticket
rt_client.update_ticket(9882, Subject='Test Ticket', custom_fields={CF.{URL}: 'http://github.com'})

# Search for existing tickets
ticket_sql = "Queue = 'General'"
tickets = rt_client.raw_search(ticket_sql)
```

## License
[Gnu GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
