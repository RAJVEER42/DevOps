# DynamoDB and RDS, the database services

Two very different answers to "where does my data live". RDS runs a relational database engine
you already know; DynamoDB is a key-value store designed around predictable performance at any
scale. Picking between them is a schema decision, not a hosting decision.

## DynamoDB

**NoSQL.** No fixed schema, no joins, no SQL. You model data around the queries you will run,
then DynamoDB promises single-digit-millisecond reads and writes at any table size, with no
servers to manage and no connection limits.

**Tables, items, attributes.** A table holds items (think rows, up to 400 KB each); an item is
a set of attributes (think columns, but each item can have different ones). Only the key
attributes are mandatory.

**Partition key.** Required. DynamoDB hashes it to decide which internal partition stores the
item. Every lookup needs it, so it must be something you always know: `user_id`, `order_id`.
A good key spreads traffic evenly; a bad one (a date, a status) sends everything to one
partition and throttles.

**Sort key.** Optional. Items with the same partition key are stored sorted by it, which enables
range queries: all orders for `user_id = 42` with `created_at` between two dates, or the
single-table pattern where one partition holds a user and all their related records under
different sort key prefixes.

```
PK (partition)   SK (sort)              attributes
USER#42          PROFILE                name, email, plan
USER#42          ORDER#2026-10-07#9f3   total, status
USER#42          ORDER#2026-10-01#1a7   total, status
```

Other pieces: secondary indexes for alternative access patterns, TTL to expire items, Streams
to react to changes, on-demand or provisioned capacity, global tables for multi-region.

**Use cases.** Session stores, shopping carts, user profiles, IoT and event ingestion,
leaderboards, Terraform state locking, anything with a known access pattern and a need to
scale without a DBA.

## RDS, Relational Database Service

**Relational database, managed.** You get a real PostgreSQL, MySQL, MariaDB, Oracle or
SQL Server (plus Aurora, AWS's own MySQL/PostgreSQL-compatible engine) on an instance AWS
patches, backs up and monitors. You still design schemas, write SQL, tune queries and manage
connections; you stop managing the OS and the backup cron.

**DB instances.** A size class (`db.t3.micro` for a lab, `db.r6g.large` for production), an
engine version, storage type and size, in a VPC subnet group spanning at least two AZs. The
endpoint is a DNS name; the application connects to it like any database.

**Security.** Lives in private subnets, never public. A security group allows the engine's
port only from the application tier's group. Encryption at rest with KMS, TLS in transit,
credentials in Secrets Manager with automatic rotation, IAM database authentication where
supported.

**Backups.** Automated daily snapshots plus transaction logs, giving point-in-time recovery to
any second within the retention window (1 to 35 days). Manual snapshots persist until deleted
and can be copied across regions and accounts.

**Multi-AZ.** A synchronous standby replica in another availability zone. Writes commit to both;
if the primary fails, DNS flips to the standby in about a minute with no data loss. It is for
availability, not read scaling, and roughly doubles the instance cost. Turn it on for anything
production.

**Read replicas.** Asynchronous copies, in the same or another region, that serve read
queries. Offload reporting and read-heavy traffic from the primary; promote one to a standalone
database for migrations or disaster recovery. Up to 15 per instance for Aurora, 5 for others.

**Use cases.** Anything with relationships, transactions and ad-hoc queries: the issue tracker
in `Issue Tracker Compose/` (PostgreSQL), billing systems, inventories, CMS back ends, and
every application whose team already thinks in SQL.

## Choosing

| Question | DynamoDB | RDS |
|---|---|---|
| Do I know every query up front? | Yes, design the keys for them | No, SQL will handle new ones |
| Joins and transactions across many tables? | Avoid | Native |
| Scale target | Millions of requests per second, automatic | Vertical first, read replicas second |
| Operations | None | Patching windows, parameter groups, connection pooling |
| Cost shape | Per request and per GB | Per instance-hour, whether busy or idle |
