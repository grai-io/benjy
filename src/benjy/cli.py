import click
import os
import shutil
from .utilities import compile_entity_graph, write_pickle, SourceRefs
from .schema import Schema


def prep_build_path(target):
    build_path = os.path.join(target, "build")
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)
    return build_path


@click.group()
@click.pass_context
def cli(ctx):
    """Entrypoint for Benjy"""
    ctx.ensure_object(dict)


@cli.command("compile")
@click.argument("target", nargs=1, type=str)
@click.pass_context
def compile(ctx, target):
    """Compile entities and build data source references from TARGET directory"""
    if not target:
        target = "."
    build_path = prep_build_path(target)
    entities_path = os.path.join(build_path, "entities.pickle")

    graph = compile_entity_graph(target)
    write_pickle(entities_path, graph)

    source_ref = SourceRefs(os.path.join(target, "data"), build_path)
    source_ref.write_source_refs()


@cli.command("submit")
@click.argument("target", nargs=1, type=str)
@click.pass_context
def submit(ctx, target):
    """Submit ETL jobs for TARGET schema file"""
    if not target:
        click.echo("submit requires a submission schema")
        return

    schema = Schema(target)

    schema.execute()


if __name__ == "__main__":
    cli(obj={})
