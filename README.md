# Look at your graph of bookmarks and tags using neo4j

## Motivation

I don't like organising my bookmarks in directories because my bookmarks often belong to several categories.
I use tags instead, that offer more flexibility.

I wanted to "see" my graph of tags and bookmarks.

## How to use

### Export your firefox bookmarks to json

In firefox, click on the `bookmarks` menu, then `Show all bookmarks`. In the new window, click on `Import and Backup` then `Backup...`. Choose where to put the file and you're done.

### Neo4j

#### What is neo4j?

[neo4j](https://neo4j.com/) is a [graph database management system](https://en.wikipedia.org/wiki/Graph_database).
You can load a graph, query it and modify it.

#### Install

[Download neo4j](https://neo4j.com/download/) and follow the installation instructions.

I use `neo4j-community-3.0.4`. I haven't tried other versions.

#### (Optional) Backup your existing Neo4j DB

The script will delete all data from the database. Back up your existing database if you want to keep it.

Check your [server config file](http://neo4j.com/docs/stable/server-configuration.html) to find the database location. The default is `<NEO4J_LOC>/data/graph.db/`. You can simply use `cp -r` or `mv`/`ln -s` to put it somewhere else.

- Make sure the server is not running when you move the files.
- The directory `<NEO4J_LOC>/data/graph.db/` must exist. It can be empty.

Alternatively, see the [neo4j-backup command](https://neo4j.com/docs/operations-manual/current/backup/perform-backup/).

#### Run neo4j

```bash
<NEO4J_LOC>/bin/neo4j start
```

The script will connect to this running instance.


### Run the script to create the neo4j DB

Requirements:

I use Python 3.5, py2neo 3.1.2 and json 2.0.9. I haven't tried different versions.

Run:

```bash
./load_bookmarks.py --input ~/Desktop/bookmarks-2017-01-01.json
```

```bash
./load_bookmarks.py --help
```

### Graph

The graph you built has 3 types of nodes:

- `bookmark`
- `tag`
- `container` for the directory structure

`container`s and `bookmark`s are linked to their parent `container`.
`bookmark`s are linked to their `tag`s.

### Watch your bookmarks

Open http://localhost:7474 in your favourite browser.
If prompted for a user/password, try the default: `neo4j`/`neo4j`.

You are in the `neo4j` browser. You can enter queries (in `cypher` language) in the top banner with a `$`.

Try this for example: `MATCH (n) RETURN n LIMIT 50`. Click the `play` button on the upper right corner to execute the query, or press `Enter` or `Ctrl+Enter`.

I recommend [styling the nodes and relationships](https://neo4j.com/developer/guide-neo4j-browser/#_styling_neo4j_browser_visualization) to get the shape of the graph at a glance.

More on [neo4j browser](https://neo4j.com/developer/guide-neo4j-browser/)
More on [cypher query language](https://neo4j.com/developer/cypher-query-language/)


#### Example of queries

Get all the nodes:

```cypher
MATCH (n) RETURN n
```

Note that by default the graph view shows all relationships between displayed nodes. So the query above will show your entire graph.

If you have lots of bookmarks, you can limit the number of returned nodes:

```cypher
MATCH (n)
RETURN n
LIMIT 100
```

---

Get the root of the bookmark directory hierarchy:

```cypher
MATCH (n:container {title:"ROOT"}) RETURN n
```

From there, double-click on nodes to get its neighbours.

---

See the bookmark directory hierarchy only, no bookmarks, no tags.

```
MATCH (c:container) RETURN c
```

---

Get the bookmarks and tags only, not directory.

```cypher
MATCH (t:tag)--(b:bookmark) RETURN t,b
```

Bookmarks with no tags are not shown.

---

Get the bookmarks that don't have tags.

```cypher
MATCH (b:bookmark)
WITH b, size((b)-->(:tag)) as degree
WHERE degree = 0
RETURN b
```

Get tags that are only used once

```cypher
MATCH (t:tag)
WITH t, size((t)<--()) as degree
WHERE degree <= 1
RETURN t
```

---

See if there are 2 directories with the same name:

```cypher
MATCH (c1:container), (c2:container)
WHERE c1.title = c2.title AND c1 <> c2
RETURN c1, c2
```

Get the tags and directories that share the same name.

```cypher
MATCH (c:container), (t:tag)
WHERE c.title = t.name
RETURN c, t
```

---

Get the bookmarks tagged with `NLP` and the directories they live in.

```cypher
MATCH (:tag {name:'NLP'}) <-- (b:bookmark) -[:has_parent*]->(c:container) RETURN b, c
```

---

Get the tags of bookmarks that are under my `tech` directory.

```cypher
MATCH (:container {title:"ROOT"}) <-- (:container {title:""}) <-- (:container {title:"Bookmarks Menu"}) <-- (:container {title:"tech"}) <-[:has_parent*0..]- (:container) <-- (:bookmark) --> (t:tag) 
RETURN t
```

## Bugs

Probably quite a lot, given that:

- there's no tests!
- I've only tried with my own bookmarks, that I use in a peculiar way. All my bookmarks live in `Bookmarks Menu`. I don't use `keyword`s,

If you find an issue, please create a github issue. Pull requests welcome.
