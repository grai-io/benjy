# Company Sales

# TODO: currently requires python / pandas to generate data. Maybe migrate this to a seperate repo and stick the data in vc.

## Getting started

First, we will need to simulate some fake data for the project. You can do that by executing the `make_data.py` script 
from this directory. We will also need to install a copy of benjy to get started.

```
pip install benjy
python make_data.py
```

Inside of the `/project` subdirectory you can see three folders:


1. `data` - this contains the raw data resources we will be writing ETL's for. In our case we have sales records coming from three different sources (a, b, and c) each with different customer identifies. We also have crosswalks between customer ids to a universal identifier shared across data sources. 
2. `entities` - these represent relationships between our data. In this case we have an entity for each customer id. These entities have a couple of attributes including the source table, the column id of the source, and a relationship between the source id and the universal id.
3. `output` - Where we are going to place out ETL output.

Finally we have a `schema.yml` file. These are declarative yaml files defining the expected output of a transformation.

## Using Benjy

In this directory, try executing the command

```
benjy compile
```

This reads the entity files defines in the `entities` subdirectory to compile a graph of relationships between our data sources. 
Benjy uses this graph to automatically produce ETL code.

Now let's look 



