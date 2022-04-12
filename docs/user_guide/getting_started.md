!!! note
    You can find also example Benjy projects [here](https://github.com/grai-io/benjy/tree/master/examples). 
    A great place to start is with the [sales](https://github.com/grai-io/benjy/tree/master/examples/sales) demo 
    you can run through live.


## Using Benjy

In order to automatically perform ETL jobs, Benjy builds a graph based model of the relationships between data throughout
your organization. These relationships are declaratively defined and version controlled - a simple entity might look like this.

```yaml
entities:
  - name: source_a_id
    source: sales_source_a_table
    column: id
    relations:
      - name: uuid
        crosswalk:
          source: crosswalk_uuid_a_table
          from: id_a
          to: uuid
```

In this case we have an `id` field on the `sales_source_a_table` that is related to a `uuid` entity via a crosswalk.
Benjy can combine these entities in complex ways to automatically produce ETL transformations for you, but first, it has
to compile this assortment of entities into a graph.

```shell
benjy compile entities
```

These compiled results are stored in the `build` subdirectory of our working directory and we are now ready to execute 
our own ETL. 

## Executing a task

ETL tasks, just like entities, are also purely declarative yaml files which can be stored in version control. Because
we've encoded so much information about our data in the form of entities, much of the traditional boilerplate of
a SQL pipeline can be stripped away leaving simple requests for the actual data we need. One example might look like
this.


```yaml
# job.yaml

target: 'output/result_table.csv'
driver: 'python'
sources:
  - 'sales_source_a_table'
  - 'sales_source_b_table'
  - 'sales_source_c_table'
name: 'aggregate_sales'
columns:
  - name: 'uuid'
    entity: 'uuid'
    origin: 'id'
    keyed: true
  - name: 'timestamp'
    origin: 'ts'
    type:
      datatype: 'timestamp'
      frequency: 4h
  - name: 'sales'
    origin: 'sales'
    type:
      datatype: 'integer'
```

Here we again have collections of data sources, a target we wish to output our job results, and a set of columns
we wish to be in our final output. We can execute this job by simply running

```bash
benjy submit job.yaml
```

## Exploring Further

!!! note
    This section will make more sense if you follow along with the live demo at [sales](https://github.com/grai-io/benjy/tree/master/examples/sales)

Much of this will be self-explanatory; We have a few sources we wish to draw data from, a location we want to place our 
result, and a name for our result. The meat of the actual query definition falls under `columns`.

First, if you look at the `uuid` column in the output file you'll see customer id's that look like `01639fb9-7bd7-43c3-afe3-b9eeef5901b7` despite
the ID's in `a`, `b` and `c` being Integers. How'd it do that? 

Each of these ids are "entities" within Benjy - basically reusable components of your organizations' data. Let's take a look
at the `source_a_id` entity in `entities/sales_source_a_table.yaml`.


```yaml
entities:
  - name: source_a_id
    source: sales_source_a_table
    column: id
    relations:
      - name: uuid
        crosswalk:
          source: crosswalk_uuid_a_table
          from: id_a
          to: uuid
```

Again, this is mostly-self explanatory - the entity, has a `name` we can reference and re-use in each ETL workflow, a `source` 
corresponding to the table it can be queried from, and the specific `column` it belongs to in the source. However, it also
has a `relations` attribute. In this case the relation describes a crosswalk between it and the universal id `uuid`.


Thanks to these entities, Benjy knows how to query for `uuid` values when provided with simple `id` from any of our three
sales sources and can perform that process for us even if it requires many steps or transformations to achieve.

There's a lot more here - try it yourself - would you prefer sales were floats rather than integers? Change the datatype to `float`. How about 
aggregating sales daily? Switch the frequency to `d`. Maybe you don't want to perform any aggregation? Remove the frequency
argument on the timestamp column and the keyed argument on uuid!
