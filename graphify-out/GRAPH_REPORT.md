# Graph Report - app  (2026-10-07)

## Corpus Check
- Corpus is ~880 words - fits in a single context window. You may not need a graph.

## Summary
- 94 nodes · 160 edges · 13 communities (5 shown, 8 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.92)
- Token cost: 51,117 input · 0 output

## Community Hubs (Navigation)
- Shipment API Endpoints
- Python Dependencies
- App Startup & Routing
- Dependency Injection
- Seller Registration API
- Database Models
- Shipment Service
- Database Config

## God Nodes (most connected - your core abstractions)
1. `ShipmentService` - 12 edges
2. `Shipment` - 9 edges
3. `ShipmentStatus` - 8 edges
4. `SellerCreate` - 7 edges
5. `ShipmentCreate` - 7 edges
6. `SellerService` - 6 edges
7. `ShipmentUpdate` - 5 edges
8. `register_seller()` - 4 edges
9. `submit_shipment()` - 4 edges
10. `update_shipment()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `SellerService` --uses--> `SellerCreate`  [INFERRED]
  services/seller.py → api/schemas/seller.py
- `ShipmentRead` --uses--> `ShipmentStatus`  [INFERRED]
  api/schemas/shipment.py → database/models.py
- `ShipmentService` --uses--> `ShipmentCreate`  [INFERRED]
  services/shipment.py → api/schemas/shipment.py
- `ShipmentUpdate` --uses--> `ShipmentStatus`  [INFERRED]
  api/schemas/shipment.py → database/models.py
- `ShipmentService` --uses--> `ShipmentStatus`  [INFERRED]
  services/shipment.py → database/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Async Postgres persistence stack** — requirements_sqlmodel, requirements_sqlalchemy, requirements_asyncpg, requirements_greenlet [INFERRED 0.85]
- **FastAPI web serving stack** — requirements_fastapi, requirements_starlette, requirements_pydantic, requirements_uvicorn [INFERRED 0.85]

## Communities (13 total, 8 thin omitted)

### Community 0 - "Shipment API Endpoints"
Cohesion: 0.22
Nodes (8): delete_shipment(), get_shipment(), submit_shipment(), update_shipment(), BaseShipment, ShipmentCreate, ShipmentRead, ShipmentUpdate

### Community 1 - "Python Dependencies"
Cohesion: 0.16
Nodes (15): asyncpg 0.31.0, bcrypt 5.0.0, email-validator 2.3.0, fastapi 0.141.1, fastapi-cli 0.0.32, greenlet 3.5.5, pydantic 2.13.5, pydantic-settings 2.15.0 (+7 more)

### Community 2 - "App Startup & Routing"
Cohesion: 0.23
Nodes (4): create_db_tables(), get_session(), get_scalar_docs(), lifespan_handler()

### Community 3 - "Dependency Injection"
Cohesion: 0.25
Nodes (3): get_seller_service(), get_shipment_service(), SellerService

### Community 4 - "Seller Registration API"
Cohesion: 0.31
Nodes (4): register_seller(), BaseSeller, SellerCreate, SellerRead

## Knowledge Gaps
- **6 isolated node(s):** `starlette 1.6.0`, `greenlet 3.5.5`, `bcrypt 5.0.0`, `python-dotenv 1.2.3`, `fastapi-cli 0.0.32` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 31 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ShipmentService` connect `Shipment Service` to `Shipment API Endpoints`, `Dependency Injection`, `Database Models`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ShipmentService` (e.g. with `ShipmentCreate` and `Shipment`) actually correct?**
  _`ShipmentService` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `starlette 1.6.0`, `greenlet 3.5.5`, `bcrypt 5.0.0` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `SellerService` connect `Dependency Injection` to `Seller Registration API`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ShipmentStatus` (e.g. with `ShipmentRead` and `ShipmentUpdate`) actually correct?**
  _`ShipmentStatus` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Why does `Shipment` connect `Shipment Service` to `App Startup & Routing`, `Database Models`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `SellerCreate` (e.g. with `register_seller()` and `SellerService`) actually correct?**
  _`SellerCreate` has 2 INFERRED edges - model-reasoned connections that need verification._