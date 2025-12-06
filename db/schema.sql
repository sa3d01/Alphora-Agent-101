CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tenants (
                         id              uuid PRIMARY KEY,
                         name            text NOT NULL
);

CREATE TABLE sops (
                      id              uuid PRIMARY KEY,
                      tenant_id       uuid REFERENCES tenants(id),
                      intent          text NOT NULL,
                      title           text NOT NULL,
                      body            text NOT NULL,
                      risk_level      text NOT NULL,
                      tags            text[],
                      created_at      timestamptz DEFAULT now(),
                      updated_at      timestamptz DEFAULT now()
);

CREATE TABLE sop_embeddings (
                                sop_id          uuid REFERENCES sops(id),
                                embedding       vector(768),
                                PRIMARY KEY (sop_id)
);
