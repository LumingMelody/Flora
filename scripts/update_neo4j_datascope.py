#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Dict, List, Tuple

from env import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from tasks.external.database.neo4j_client import Neo4jClient


def load_updates(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, list):
        raise ValueError("JSON root must be a list")

    rows: List[Dict[str, str]] = []
    index: Dict[str, int] = {}
    for item in payload:
        props = item.get("n", {}).get("properties", {})
        node_id = props.get("id")
        if not node_id:
            continue
        datascope = props.get("datascope")
        if datascope is None:
            datascope = ""
        elif not isinstance(datascope, str):
            datascope = json.dumps(datascope, ensure_ascii=False)

        if node_id in index:
            rows[index[node_id]]["datascope"] = datascope
        else:
            index[node_id] = len(rows)
            rows.append({"id": node_id, "datascope": datascope})

    return rows


def update_batch(
    client: Neo4jClient,
    rows: List[Dict[str, str]],
    report_missing: bool,
) -> Tuple[int, List[str]]:
    update_query = """
    UNWIND $rows AS row
    MATCH (a:Agent {id: row.id})
    SET a.datascope = row.datascope
    RETURN count(a) AS updated
    """
    result = client.execute_write(update_query, {"rows": rows})
    updated = int(result.get("updated", 0)) if result else 0

    missing: List[str] = []
    if report_missing:
        find_query = """
        UNWIND $rows AS row
        MATCH (a:Agent {id: row.id})
        RETURN a.id AS id
        """
        found = client.execute_query(find_query, {"rows": rows})
        found_ids = {r["id"] for r in found}
        missing = [row["id"] for row in rows if row["id"] not in found_ids]

    return updated, missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update datascope fields in Neo4j from a records JSON file."
    )
    parser.add_argument(
        "--json",
        default="dify_workflow/records (1).json",
        help="Path to records JSON file.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="Number of nodes to update per batch.",
    )
    parser.add_argument(
        "--report-missing",
        action="store_true",
        help="Report node IDs that do not exist in Neo4j.",
    )
    parser.add_argument("--neo4j-uri", default="", help="Override NEO4J_URI.")
    parser.add_argument("--neo4j-user", default="", help="Override NEO4J_USER.")
    parser.add_argument("--neo4j-password", default="", help="Override NEO4J_PASSWORD.")

    args = parser.parse_args()

    uri = args.neo4j_uri or NEO4J_URI
    user = args.neo4j_user or NEO4J_USER
    password = args.neo4j_password or NEO4J_PASSWORD
    if not uri or not user or not password:
        print("Missing Neo4j config. Set NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD.", file=sys.stderr)
        return 2

    rows = load_updates(args.json)
    if not rows:
        print("No nodes found in JSON.")
        return 1

    client = Neo4jClient(uri=uri, user=user, password=password)
    total_updated = 0
    missing_ids: List[str] = []
    try:
        for start in range(0, len(rows), args.batch_size):
            batch = rows[start : start + args.batch_size]
            updated, missing = update_batch(client, batch, args.report_missing)
            total_updated += updated
            missing_ids.extend(missing)
    finally:
        client.disconnect()

    print(f"Updated nodes: {total_updated}/{len(rows)}")
    if args.report_missing and missing_ids:
        print("Missing node IDs:")
        for node_id in missing_ids:
            print(node_id)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
