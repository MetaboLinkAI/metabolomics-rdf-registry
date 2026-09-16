# Metabolomics RDF Endpoint Registry

A community-maintained catalogue of RDF/SPARQL endpoints relevant to metabolomics research. This catalog powers the automatic generation of the **KGHub map**: an high-level, schema-like representation of metabolomics RDF resources, to simplify resource discovery and federated querying.

## How it works

Each endpoint is one YAML file in [`data/endpoints/`](data/endpoints/),
following the schema in [`schema/endpoint.schema.json`](schema/endpoint.schema.json).
metadata lives in plain text files under version control, and changes go through
normal PR review.

## How to suggest an endpoint

Open a [new issue using the submission form](../../issues/new?template=new-endpoint.yml)
and fill in the fields.

## Acknowledgment

This work is part of the [MetaboLinkAI](https://www.metabolinkai.net/) project co-funded by the Swiss National Science Foundation (SNF 10002786) and the French Agence Nationale de la Recherche (ANR-24-CE93-0012-01).

