import json
import os
import traceback
from typing import List, Dict, Tuple, Optional
from node_path import NodePath

def load_raw_workspace(workspace_path):
    with open(workspace_path, "r") as fl:
        return json.load(fl)

def get_node_dict(workspace):

    if '_node_dict_' not in workspace:

        result = {}
        for node in workspace["dialog_nodes"]:
            result[node["dialog_node"]] = node
        workspace['_node_dict_'] = result
    return workspace['_node_dict_']

def get_parents_of_nodes_with_intent(workspace, intent):

    result = {}
    for node in workspace["dialog_nodes"]:
        # todo we can later add nodes with complex conditions
        if node.get("conditions", "").strip() == "#" + intent:
            parent = get_parent(workspace, node)
            result[parent["dialog_node"]] = parent
    return list(result.values())

def get_parent(workspace, node):

    nodes = get_node_dict(workspace)

    if "parent" in node:
        return nodes[node["parent"]]
    else:
        return node['root']

def get_output_paths(workspace, node):

    result = []
    for child in get_graph_children(workspace, node):

        output_text = get_output_text(child)
        if output_text:
            result.append(NodePath([node, child]))

    return result

def get_graph_children(workspace, parent):

    parent_id = parent["dialog_node"]
    result = []

    for node in workspace["dialog_nodes"]:
        if node.get("parent", 'root_node') == parent_id:
            result.append(node)

    return result

def add_all_children_to_parents(workspace):
	nodes_with_childrens = []
	nodes = {'root': 'root', 'children': []}
	lst = [d['dialog_node'] for d in workspace['dialog_nodes']]
	lst = sorted(lst)

	for i in workspace['dialog_nodes']:
		graph = get_graph_children(workspace, i)
		if len(graph) == 0:
			nodes['children'].append({'dialog_node': i['dialog_node'], 'n._of_conversations': 0, 'children': []})
			continue
		
		for j in graph:
			idx = find_node(nodes['children'], i['dialog_node'])
			if idx == -1:
				if 'previous_sibling' in j:
					nodes['children'].append({'dialog_node': i['dialog_node'], 'n._of_conversations': 0, 'children': [{'dialog_node': j['dialog_node'],'output': j['output'], 'previous_sibling': j['previous_sibling']}]})
				else:
					nodes['children'].append({'dialog_node': i['dialog_node'], 'n._of_conversations': 0, 'children': [{'dialog_node': j['dialog_node'], 'output': j['output']}]})
			else:
				if 'previous_sibling' in j:
					nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'output': j['output'], 'previous_sibling': j['previous_sibling']})
				else:
					nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'output': j['output']})
			
#	for node in nodes['children']:
#		if len(node['children']) > 1:
#		tmp = {}
#			for j in node['children']:
#				if 'previous_sibling' not in j:
#					tmp['firs_child'] = j['dialog_node']
#				else:
#					tmp[j['previous_sibling']] = j['dialog_node']
#			childs = [tmp['first']]
#			node = tmp['first']
#			del tmp['first']
#			for i in tmp:
#				childs.append(tmp[node])
#				node = tmp[node]
				

	return nodes


def compute_number_of_conversations(tree, logs):
	nodes = []
	for i in logs:
		nodes.append(i['response']['output']['nodes_visited'])
	nodes.sort(key=len)
	# TODO: 
#	for node in nodes:
#		idx = find_node(tree['children'], node[0])
#		print(node[0]) 				
#		tree['children'][idx]['n._of_conversations'] += 1
		#if len(node) > 1:
		#	for i in range(1, len(node)):
		#			idx2 = find_node(tree['children'][idx]['children'], node[i])
		#		if idx2 == -1: 
	#				print(node[i]) 
				#	continue
	#			if 'n._of_conversations' in tree['children'][idx]['children'][idx2]:
	#				tree['children'][idx]['children'][idx2]['n._of_conversations'] += 1
#				else: tree['children'][idx]['children'][idx2]['n._of_conversations'] = 1

	return tree


def get_direct_output_children(workspace, node, skip_output=False):

    if not skip_output and "output" in node:
        return [node]

    next_step = node.get("next_step", None)

    if not next_step:

        return []

    nodes = get_node_dict(workspace)

    behavior = next_step["behavior"]

    if behavior == "jump_to":
        return get_direct_output_children(workspace, nodes[next_step["dialog_node"]])

def find_node(lst, node):

	for i,d in enumerate(lst):
		if d['dialog_node'] == node:
			return i
	return -1

