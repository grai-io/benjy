
A Benjy configuration is a collection of pre-defined data relationships (or entities)
used to build and automate data transformations. Entities are compiled together through
the cli to build a graph defining the relationships between data across your organization.

A basic project configuration would look something like

```
configuration
|-- data
|-- entities
|-- build
```

## Building your configuration

!!! note
    Configurations are currently limited to local directories. As we rollout cloud deployed
    instances of Benjy you will be able to set and reuse configurations through the cli.


Only the `entities` folder is strictly required in a new Benjy project, others like the
`build` folder will be created for you when you compile your configuration. When you're 
done building entities it's a simple as calling `compile` on your configuration folder.

```bash
benjy compile configuration/
```

Once you've called compile you should find two files in the `build/` subdirectory. 
At this point you're ready to roll!

