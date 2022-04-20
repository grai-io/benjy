Schemas define a full ELT workflow.
It specifies the source data to extract and what you expect the end result to look like.
If you wanted to duplicate the sales table from a transactional database into your
warehouse you would write a schema file roughly like this.

!!! note
    Data integration handling will come with the cloud docker deployment. All of these
    capabilities can be tested locally for the moment.

```yaml
target: warehouse
sources: sales_table
name: 'extracted_sales_table'
columns: *
```

Going back to the previous `customer_id` example, you might want to export `sales_table`
while also including a `uuid` column. In this case we would simply add a column into
the schema file referencing the defined `uuid` entity.

```yaml
target: warehouse
sources: sales_table
name: 'extracted_sales_table'
columns: 
  - name: 'uuid'
    entity: 'uuid'
    origin: 'customer_id'
  - *
```

We can also perform a variety of aggregations and other operations within these schemas. 
If you're interested in seeing a few of these live checkout some of our examples on 
[github](https://github.com/grai-io/benjy).
