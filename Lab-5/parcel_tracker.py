"""Courier & parcel tracking system.

Books parcels with tracking ids, moves them through the delivery stages,
tracks a parcel by id, checks whether it is still with the courier,
generates a delivery OTP and works out the shipping cost by weight.
"""
import os
import re
import secrets
import shutil
import subprocess  # nosec B404 - only used with a fixed argv list, no shell
import tempfile
from datetime import date

STATUS_FLOW = ["Booked", "Picked Up", "In Transit",
               "Out for Delivery", "Delivered"]
parcels = {}


def book_parcel(sender, receiver, weight_kg, history=None):
    """Book a parcel and return its new tracking id.

    If ``history`` (a list) is given, the id is appended to it. A fresh list
    is created per call when omitted, so state is never shared between calls.
    """
    if history is None:
        history = []
    tracking_id = "TRK" + str(10001 + len(parcels))
    parcels[tracking_id] = {"sender": sender, "receiver": receiver,
                            "weight": weight_kg, "status": 0,
                            "booked": str(date.today())}
    history.append(tracking_id)
    return tracking_id


def advance_status(tracking_id):
    """Move a parcel to its next stage (stops at Delivered); return it."""
    parcel = parcels[tracking_id]
    if parcel["status"] < len(STATUS_FLOW) - 1:
        parcel["status"] += 1
    return STATUS_FLOW[parcel["status"]]


def shipping_cost(weight_kg):
    """Return the shipping cost: 50 base, plus 30 per kg above the first."""
    cost = 50
    if weight_kg > 1:
        cost += (weight_kg - 1) * 30
    return round(cost, 2)


def track_parcel(tracking_id):
    """Return 'sender -> receiver: stage', or a message for an unknown id."""
    try:
        parcel = parcels[tracking_id]
    except KeyError:
        return "Unknown tracking id " + tracking_id
    route = parcel["sender"] + " -> " + parcel["receiver"]
    return route + ": " + STATUS_FLOW[parcel["status"]]


def is_with_courier(tracking_id):
    """Return True while the parcel is Picked Up or In Transit."""
    status = STATUS_FLOW[parcels[tracking_id]["status"]]
    return status in ("Picked Up", "In Transit")


def label_path():
    """Create an empty temporary label file and return its path."""
    # Helper kept for the lab: not called by the demo
    # mkstemp creates the file atomically (mktemp only invents a name, which
    # is racy); close the open descriptor and hand back just the path.
    file_descriptor, path = tempfile.mkstemp(suffix=".txt")
    os.close(file_descriptor)
    return path


# Hostname / IP: must start with a letter or digit so it can never be read
# as a command-line option (e.g. "-f"), and may not contain shell characters.
HOST_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]{0,252}$")


def ping_hub(hub_address):
    """Ping a hub once and return the raw ping output.

    Raises ValueError for an address that is not a plain hostname or IP.
    """
    # Helper kept for the lab: not called by the demo
    if not HOST_PATTERN.match(hub_address):
        raise ValueError("Invalid hub address: " + repr(hub_address))
    ping_binary = shutil.which("ping")
    if ping_binary is None:
        raise FileNotFoundError("ping executable not found")
    # Argument list and no shell: the address is never interpreted by a shell.
    return subprocess.check_output(  # nosec B603
        [ping_binary, "-c", "1", hub_address])


def main():
    """Run a short demonstration of the tracker."""
    first = book_parcel("Bengaluru Books", "Ravi Kumar", 2.5)
    second = book_parcel("Gadget Hub", "Sneha Rao", 0.8)
    third = book_parcel("Spice Store", "Imran Khan", 4)
    advance_status(first)
    advance_status(first)
    advance_status(second)
    for _ in range(6):
        advance_status(third)
    for tracking_id in (first, second, third):
        print(track_parcel(tracking_id))
        print("  with courier:", is_with_courier(tracking_id))
        print("  cost:", shipping_cost(parcels[tracking_id]["weight"]))
    print(track_parcel("TRK00000"))  # unknown id
    # secrets (CSPRNG) instead of random: an OTP must be unpredictable.
    delivery_otp = 1000 + secrets.randbelow(9000)  # 1000..9999 inclusive
    print("Delivery OTP for", third, "is", delivery_otp)
    print("Parcels booked today:", len(parcels))


if __name__ == "__main__":
    main()
