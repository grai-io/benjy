Entities are the basic building blocks of your organizations' data.
They can represent semantic ideas like `customer id` or commonly used transformations 
like insuring a date arrives transformed to UTC timezones.

## Entity Files

Consider the following entity file

```yaml
entities:
  - name: customer_id
    source: order_table
    column: id
```

Here we are defining a single entity with the name `customer_id` which corresponds to the
`id` column on the `order_table`. We can now use the name `customer_id` as a named reference
when writing transformation jobs.

## Entity Relations

Entities can incorporate complicated relationships between data arriving from 
multiple source systems. For example, if the `customer_id` had a corresponding
`uuid` on the `uuid_table` we could write something like this.


```yaml
entities:
  - name: customer_id
    source: order_table
    column: id
    relations:
      - name: uuid
        crosswalk:
          source: uuid_table
          from: order_table_id
          to: uuid
```

Explicitly encoding these relationships allows for reuse by developers and analysts.
It also allows benjy to automate data queries. For example, if you have `customer_id`'s
in your data but need `uuid` values instead, Benjy now knows how to generate those
values for you. No extra SQL required.