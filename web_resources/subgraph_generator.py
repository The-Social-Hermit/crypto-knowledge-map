"""
subgraph_generator.py
01/17/22
Contributors: Levi Purdy

This script is used to prepare the obsidian markdown notes for web publication.
It is intended to be run from the command line.

This script will scan the wikilinks in a collection of markdown files and generate subgraphs
of the wikilinks in each file.

Some code may have been generated by OpenAI's davinci-codex.
This is low quality code. It has a O(n^2) time complexity. It is not intended to be used for large werbsites.
"""

# Sample mermaid graph:
"""
```mermaid
graph LR
    A["What is git"]-->B{"How do cryptocurrencies change"}
    C["What is an update"]-->B
    D["What is a hard fork"]-->B
    B-->E["How to keep up with change"]
```
"""

import glob

subgraph_section_string = "# Subgraph"


def strip_brackets(string):
    """
    Strips brackets from a string.
    """
    return string.replace('[', '').replace(']', '')


def find_wikilinks(file_path):
    """
    Returns a list of wikilinks in a markdown file.
    Only searches after the "# Prerequisites" section and before the "# Description" section

    """
    found_prereqs = False
    wikilinks = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('# Prerequisites'):
                found_prereqs = True
                continue
            if found_prereqs and line.startswith('# Description'):
                break
            elif found_prereqs and line.startswith('[['):
                nice_file_name = strip_brackets(line.strip())
                nice_file_name = nice_file_name.replace('_', ' ')
                wikilinks.append(nice_file_name)
    return wikilinks


def gen_expected_filename(file_name):
    file_name_expected = file_name.split('/')[-1]
    file_name_expected = file_name_expected.replace('_', ' ')
    file_name_expected = file_name_expected.split('.')[0]

    return file_name_expected


def find_backlinks(directory, file_name):
    """
    Returns a list of wikilinks referencing file_name in all other markdown files in directory

    Needs to replace underscores with spaces in md_file before appending to list.
    """
    # gen expected file name
    file_name_expected = gen_expected_filename(file_name)
    backlinks = []
    md_file_list = list_markdown_files(directory)
    for md_file in md_file_list:
        with open(md_file, 'r') as f:
            found_prereqs = False
            for line in f:
                if line.startswith('# Prerequisites'):
                    found_prereqs = True
                    continue
                if found_prereqs and line.startswith('# Description'):
                    break
                elif found_prereqs and line.startswith('[['):
                    if file_name_expected in line:
                        md_file_readable = md_file.replace('_', ' ')
                        md_file_readable = md_file_readable.split('.')[0]
                        md_file_readable = md_file_readable.split('/')[-1]
                        backlinks.append(md_file_readable)
    return backlinks


def list_markdown_files(directory):
    """
    Returns a list of markdown files in a directory.
    """
    # 1. Create a list of all markdown (.md) files contained in a folder recursively using glob
    md_files = glob.glob(directory+"/*.md")
    return md_files


def encapsulate_name(name):
    """
    Encapsulates a string in quotes and brackets
    """
    return '[\"'+name+'\"]'


def generate_subgraph(wikilinks, file_name, backlinks):
    """
    Generates a mermaid graph from a list of wikilinks and a list of backlinks.
    # Sample mermaid graph:
    ```mermaid
    graph LR
    1["What is git"]-->0{"How do cryptocurrencies change"}
    2["What is an update"]-->0
    3["What is a hard fork"]-->0
    0-->4["How to keep up with change"]
    ```
    """
    line_string = '-->'
    connected_iterator = 1
    current_page_id = 0
    # use expected file name
    current_page_name = str(current_page_id)+'{\"'+gen_expected_filename(file_name)+'\"}'

    graph = "```mermaid\ngraph LR\n"
    for link in wikilinks:
        graph += str(connected_iterator)+encapsulate_name(link)+line_string+current_page_name+"\n"
        connected_iterator += 1
    for backlink in backlinks:
        graph += current_page_name+line_string+str(connected_iterator)+encapsulate_name(backlink)+"\n"
        connected_iterator += 1
    graph += "```\n\n"
    return graph


def insert_graph(graph, file_name):
    """
    Inserts a mermaid graph into a markdown file.
    Cases:
    Graph exists and needs to be replaced
    Graph does not exist and needs to be inserted
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()

    found_subgraph = False
    with open(file_name, 'w') as f:
        for line in lines:
            if line.startswith(subgraph_section_string):
                # if graph exists, don't write lines until description section is found
                found_subgraph = True
                continue
            if line.startswith('# Description'):
                found_subgraph = False
                f.write(subgraph_section_string + "\n\n")
                f.write(graph)
                f.write("\n\n")
                f.write(line)
            elif not found_subgraph:
                f.write(line)


def main():
    md_files_directory = "../notes"
    md_file_list = list_markdown_files(md_files_directory)

    # TODO: fix "A Learning Order" showing up in backlinks. Something wrong with prerequisites exclusion
    for md_file in md_file_list:
        wikilinks = find_wikilinks(md_file)
        backlinks = find_backlinks(md_files_directory, md_file)
        graph = generate_subgraph(wikilinks, md_file, backlinks)
        if len(wikilinks) > 0 or len(backlinks) > 0:
            insert_graph(graph, md_file)


if __name__ == "__main__":
    main()