#!/usr/bin/env python3

import json
from py2neo import Node, Relationship, Graph


def delete_all_data(graph):
    graph.delete_all()

    for label in graph.node_labels:
        print(label)
        for constraint in graph.schema.get_uniqueness_constraints(label):
            graph.schema.drop_uniqueness_constraint(label, constraint)
            print('dropped uniqueness constraint on {} {}'.format(label, constraint))
        for index in graph.schema.get_indexes(label):
            graph.schema.drop_index(label, index)
            print('dropped index on {} {}'.format(label, index))


def process_bookmark(g, leaf, parent_container_node):
    n = Node('bookmark', title=leaf.get('title'), uri=leaf['uri'], bookmark_id=leaf['id'], guid=leaf['guid'])
    graph.create(n)
    rel = Relationship(n, 'has_parent', parent_container_node)
    graph.create(rel)
    tags = leaf['tags'].split(',') if 'tags' in leaf else []
    for tag_name in tags:
        t = Node('tag', name=tag_name)
        g.merge(t)
        rel = Relationship(n, 'has_tag', t)
        g.create(rel)


def process_container(g, container, parent_container_node):
    n = Node(
        'container',
        root=container.get('root'),
        container_id=container['id'],
        title=container['title'],
        guid=container['guid']
    )
    g.create(n)
    rel = Relationship(n, 'has_parent', parent_container_node)
    g.create(rel)
    return n


def is_regular_bookmark(j):
    # by "regular", I mean "not smart bookmark"
    return j['type'] == 'text/x-moz-place' and not j['uri'].startswith('place:')


def is_container(j):
    return j['type'] == 'text/x-moz-place-container'


def create_nodes_and_rels(g, j, parent_container_node=None):

    if parent_container_node is None:
        parent_container_node = Node('container', title='ROOT')

    if is_regular_bookmark(j):
        process_bookmark(g, j, parent_container_node)
    elif is_container(j):
        parent_container_node = process_container(g, j, parent_container_node)
        for child in j.get('children', []):
            create_nodes_and_rels(g, child, parent_container_node)


def prepare_graph(graph):
    # uniqueness constraints create indexes
    graph.schema.create_uniqueness_constraint('container', 'container_id')
    graph.schema.create_uniqueness_constraint('container', 'guid')
    graph.schema.create_uniqueness_constraint('bookmark', 'bookmark_id')
    graph.schema.create_uniqueness_constraint('bookmark', 'guid')


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        '--input', dest='input',
        help='Json dump of bookmarks produced by Firefox', metavar='file_name')
    parser.add_option(
        '--host', dest='host', default='localhost',
        help='neo4j host ip', metavar='str')
    parser.add_option(
        '--port', dest='port', default=7474,
        help='neo4j http port', metavar='int')
    parser.add_option(
        '--user', dest='user', default='neo4j',
        help='neo4j user', metavar='str')
    parser.add_option(
        '--password', dest='password', default='neo4j',
        help='neo4j user password', metavar='str')

    (options, args) = parser.parse_args()

    if options.input is None:
        print('input is required')
        parser.print_help()
        exit(1)

    graph = Graph(
        host=options.host,
        http_port=options.port,
        user=options.user,
        password=options.password
    )
    delete_all_data(graph)

    prepare_graph(graph)

    with open(options.input) as f:
        dump = json.load(f)

    create_nodes_and_rels(graph, dump)
