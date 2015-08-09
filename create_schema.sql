-- Table: industry
--DROP TABLE industry;
CREATE TABLE industry
(
  id integer NOT NULL,
  alias character varying,
  CONSTRAINT "industry primary key" PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Table: period sequence
CREATE SEQUENCE public.time_id_seq
  INCREMENT 1
  START 1;
  
-- Table: period
-- DROP TABLE period;
CREATE TABLE period
(
  id serial NOT NULL,
  simyear integer,
  simmonth smallint,
  simweek smallint,
  simday smallint,
  CONSTRAINT "time primary key" PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Table: owner
-- DROP TABLE owner;
CREATE TABLE owner
(
  id serial NOT NULL,
  alias character varying,
  email character varying,
  whsespace smallint DEFAULT 1000,
  population integer DEFAULT 1000,
  starttimeid integer,
  CONSTRAINT "owner primary key" PRIMARY KEY (id),
  CONSTRAINT "owner start time" FOREIGN KEY (starttimeid)
      REFERENCES period (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

-- Table: business
-- DROP TABLE business;
CREATE TABLE business
(
  id serial NOT NULL,
  industryid integer NOT NULL,
  ownerid integer NOT NULL,
  alias character varying,
  starttimeid integer,
  produnits integer NOT NULL DEFAULT 1, -- used for factories/farms
  CONSTRAINT "business primary key" PRIMARY KEY (id),
  CONSTRAINT "biz industry key" FOREIGN KEY (industryid)
      REFERENCES industry (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "biz owner key" FOREIGN KEY (ownerid)
      REFERENCES owner (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "biz period id" FOREIGN KEY (starttimeid)
      REFERENCES period (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
COMMENT ON COLUMN business.produnits IS 'used for factories/farms';

-- Table: demand
-- DROP TABLE demand;
CREATE TABLE demand
(
  id serial NOT NULL,
  industryid integer NOT NULL,
  multiplier real,
  timeid integer,
  units integer,
  CONSTRAINT "demand primary key" PRIMARY KEY (id),
  CONSTRAINT "demand industry id" FOREIGN KEY (industryid)
      REFERENCES industry (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "demand time id" FOREIGN KEY (timeid)
      REFERENCES period (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

-- Table: inventory
-- DROP TABLE inventory;
CREATE TABLE inventory
(
  id serial NOT NULL,
  units integer,
  price real,
  businessid integer,
  timeid integer,
  CONSTRAINT "inventory primary key" PRIMARY KEY (id),
  CONSTRAINT "inventory business id" FOREIGN KEY (businessid)
      REFERENCES business (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "inventory time id" FOREIGN KEY (timeid)
      REFERENCES period (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

-- Table: ledger
-- DROP TABLE ledger;
CREATE TABLE ledger
(
  id serial NOT NULL,
  businessid integer,
  account text,
  timeid integer,
  amount real,
  CONSTRAINT "ledger primary key" PRIMARY KEY (id),
  CONSTRAINT "ledger business id" FOREIGN KEY (businessid)
      REFERENCES business (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "ledger time id" FOREIGN KEY (timeid)
      REFERENCES period (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

-- Table: supply
-- DROP TABLE supply;
CREATE TABLE supply
(
  id serial NOT NULL,
  timeid integer NOT NULL,
  endunits integer,
  wipunits integer,
  industryid integer,
  CONSTRAINT "supply primary key" PRIMARY KEY (id),
  CONSTRAINT "supply industry id" FOREIGN KEY (industryid)
      REFERENCES industry (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "supply time id" FOREIGN KEY (timeid)
      REFERENCES period (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);