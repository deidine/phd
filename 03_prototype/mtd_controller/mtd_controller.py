"""
MTD Controller for Kubernetes Microservices
Contribution 1 of PhD Thesis: Moving Target Defense Engine (MKE)

Author: Deidine Cheigeur
Date: 2026
GitHub: phd-mtd-zanzibar-security

Description:
    Periodically rotates Kubernetes service ClusterIPs and port assignments
    to implement Moving Target Defense. Service discovery is maintained
    via Ory Keto relationship tuples (dynamic service registry).

References:
    - Sengupta et al. (2020) IEEE CSTUT: https://doi.org/10.1109/COMST.2020.2982955
    - Jajodia et al. (2011) MTD: https://link.springer.com/book/10.1007/978-1-4614-0977-9
    - Ory Keto docs: https://www.ory.sh/docs/keto/

Requirements:
    pip install kubernetes requests
    kubectl access to a running cluster
"""

import time
import random
import logging
import requests
from kubernetes import client, config
from dataclasses import dataclass
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MTD] %(levelname)s %(message)s"
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────

ROTATION_INTERVAL   = 60          # seconds between rotations
PORT_RANGE          = (30000, 32767)  # NodePort range
KETO_WRITE_URL      = "http://keto:4467"  # Keto write API
KETO_READ_URL       = "http://keto:4466"  # Keto read API
NAMESPACE           = "default"
DISRUPTION_BUDGET   = 0.01        # max 1% legitimate requests may fail during rotation


@dataclass
class ServiceRecord:
    name: str
    old_port: int
    new_port: int
    rotation_time: float


# ── Keto Integration ──────────────────────────────────────────────

def update_keto_tuple(service_name: str, new_port: int) -> bool:
    """
    Update the Keto authorization tuple to reflect the new service port.
    Legitimate clients query Keto to discover the current port — not DNS.
    This is the key integration: MTD + authorization as unified registry.

    Tuple structure:
        object:  service:{service_name}
        relation: exposes_port
        subject: port:{new_port}
    """
    # Delete old port tuple
    try:
        requests.delete(
            f"{KETO_WRITE_URL}/admin/relation-tuples",
            json={
                "namespace": "services",
                "object": service_name,
                "relation": "exposes_port",
            },
            timeout=5
        )
    except requests.RequestException as e:
        log.warning(f"Could not delete old Keto tuple for {service_name}: {e}")

    # Create new port tuple
    payload = {
        "namespace": "services",
        "object": service_name,
        "relation": "exposes_port",
        "subject_id": str(new_port),
    }
    try:
        resp = requests.put(
            f"{KETO_WRITE_URL}/admin/relation-tuples",
            json=payload,
            timeout=5
        )
        resp.raise_for_status()
        log.info(f"Keto updated: {service_name} → port {new_port}")
        return True
    except requests.RequestException as e:
        log.error(f"Failed to update Keto tuple for {service_name}: {e}")
        return False


# ── Kubernetes Operations ─────────────────────────────────────────

def get_services(v1: client.CoreV1Api) -> list:
    """Return all NodePort services in the namespace that are MTD-managed."""
    services = v1.list_namespaced_service(namespace=NAMESPACE)
    return [
        svc for svc in services.items
        if svc.metadata.labels and svc.metadata.labels.get("mtd-managed") == "true"
    ]


def rotate_service_port(v1: client.CoreV1Api, service_name: str) -> Optional[ServiceRecord]:
    """
    Rotate the NodePort of a service to a new random port.
    Returns a ServiceRecord on success, None on failure.
    """
    try:
        svc = v1.read_namespaced_service(name=service_name, namespace=NAMESPACE)
    except client.exceptions.ApiException as e:
        log.error(f"Cannot read service {service_name}: {e}")
        return None

    old_port = svc.spec.ports[0].node_port
    new_port = random.randint(*PORT_RANGE)

    # Avoid collision with existing ports
    existing_services = get_services(v1)
    used_ports = {
        p.node_port
        for s in existing_services
        for p in (s.spec.ports or [])
        if p.node_port
    }
    while new_port in used_ports:
        new_port = random.randint(*PORT_RANGE)

    # Patch the service
    patch = {"spec": {"ports": [{"port": svc.spec.ports[0].port,
                                  "nodePort": new_port,
                                  "protocol": "TCP"}]}}
    try:
        v1.patch_namespaced_service(name=service_name, namespace=NAMESPACE, body=patch)
        log.info(f"Rotated {service_name}: {old_port} → {new_port}")
        return ServiceRecord(
            name=service_name,
            old_port=old_port,
            new_port=new_port,
            rotation_time=time.time()
        )
    except client.exceptions.ApiException as e:
        log.error(f"Failed to patch service {service_name}: {e}")
        return None


# ── Main MTD Loop ─────────────────────────────────────────────────

def run_mtd_controller():
    """
    Main control loop. Every ROTATION_INTERVAL seconds:
    1. List all MTD-managed services
    2. Rotate each service port to a new random value
    3. Update Keto authorization tuples with new ports
    4. Log the rotation event for the statistical detector
    """
    config.load_incluster_config()   # use in-cluster config when running in a pod
    v1 = client.CoreV1Api()

    log.info(f"MTD Controller started. Rotation interval: {ROTATION_INTERVAL}s")
    log.info(f"Sengupta et al. (2020): doi.org/10.1109/COMST.2020.2982955")

    rotation_count = 0

    while True:
        services = get_services(v1)
        if not services:
            log.warning("No MTD-managed services found. Label services with mtd-managed=true")
            time.sleep(ROTATION_INTERVAL)
            continue

        rotation_count += 1
        log.info(f"=== Rotation #{rotation_count} — {len(services)} services ===")

        records = []
        for svc in services:
            record = rotate_service_port(v1, svc.metadata.name)
            if record:
                keto_ok = update_keto_tuple(record.name, record.new_port)
                if keto_ok:
                    records.append(record)

        log.info(f"Rotation #{rotation_count} complete: "
                 f"{len(records)}/{len(services)} services rotated successfully")

        # Write rotation log for statistical detector
        with open("/var/log/mtd/rotation.log", "a") as f:
            for r in records:
                f.write(f"{r.rotation_time:.3f},{r.name},{r.old_port},{r.new_port}\n")

        time.sleep(ROTATION_INTERVAL)


if __name__ == "__main__":
    run_mtd_controller()
