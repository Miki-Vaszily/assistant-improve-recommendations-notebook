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
			if 'title' in i:
				nodes['children'].append({'dialog_node': i['dialog_node'], 'n_of_conversations': 0, 'children': [], 'name': i['title'], 'type': i['type']})
			elif 'conditions' in i:
				nodes['children'].append({'dialog_node': i['dialog_node'], 'n_of_conversations': 0, 'children': [], 'name': i['conditions'], 'type':i['type']})
			else:
				nodes['children'].append({'dialog_node': i['dialog_node'], 'n_of_conversations': 0, 'children': [], 'name': 'response_condition', 'type':i['type']})

			continue
		
		for j in graph:
			idx = find_node(nodes['children'], i['dialog_node'])
			if idx == -1:
				if 'previous_sibling' in j:
					if 'title' in i and 'title' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name':i['title'] ,'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': j['title']}]})

					elif 'title' in i:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name':i['title'] ,'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': j['conditions']}]})

					elif 'title' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name':i['conditions'] ,'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': j['title']}]})

					elif 'conditions' in i and 'conditions' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': i['conditions'], 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': j['conditions']}]})

					elif 'conditions' in i:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':j['type'], 'n_of_conversations': 0, 'name': i['conditions'], 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': 'response_condition'}]})

					elif 'conditions' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': 'response_condition', 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': j['conditions']}]})

					else:						
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': 'response_condition', 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name':'response_condition'}]})

						
				else:
					if 'title' in i and 'title' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type': i['type'], 'n_of_conversations': 0, 'name': i['title'],'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': j['title']}]})

					elif 'title' in i:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type': i['type'], 'n_of_conversations': 0, 'name': i['title'], 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': j['conditions']}]})

					elif 'title' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': i['conditions'], 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': j['title']}]})

					elif 'conditions' in i and 'conditions' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': i['conditions'], 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': j['conditions']}]})

					elif 'conditions' in i:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'],'n_of_conversations': 0, 'name': i['conditions'], 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': 'response_condition'}]})

					elif 'conditions' in j:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': 'response_condition', 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': j['conditions']}]})

					else:
						nodes['children'].append({'dialog_node': i['dialog_node'], 'type':i['type'], 'n_of_conversations': 0, 'name': 'response_condition', 'children': [{'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0,'output': j['output'], 'name': 'response_condition'}]})

			else:
				if 'previous_sibling' in j:
					if 'title' in j:
						nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations': 0,'output': j['output'], 'previous_sibling': j['previous_sibling'], 'name': j['title']})
					elif 'conditions' in j:
						nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0, 'output': j['output'], 'previous_sibling':j['previous_sibling'], 'name': j['conditions']})
					else:
						nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations':0, 'output': j['output'], 'previous_sibling':j['previous_sibling'], 'name': 'response_condition'})

				else:
					if 'title' in j:
						nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'type':j['type'],'n_of_conversations': 0,'output': j['output'], 'name':j['title']})
					elif 'conditions' in j:
						nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'type':j['type'],'n_of_conversations': 0,'output': j['output'], 'name': j['conditions']})
					else:
						nodes['children'][idx]['children'].append({'dialog_node': j['dialog_node'], 'type':j['type'], 'n_of_conversations': 0,'output': j['output'], 'name': 'response_condition'})


	for i in nodes['children']:
		if len(i['children']) > 1:
			helper = {}
			for j in i['children']:
				if 'previous_sibling' not in j:
					helper['first'] = j
				else:
					helper[j['previous_sibling']] = j
				
			i['children'] = [helper['first']]
			nd = helper['first']['dialog_node']
			del helper['first'] 
			while len(helper) > 0:
				nd = i['children'][-1]['dialog_node']
				i['children'].append(helper[nd])
				del helper[nd]	

	return nodes


def compute_number_of_conversations(tree, logs):
	nodes = []
	for i in logs:
		nodes.append(i['response']['output']['nodes_visited'])
	nodes.sort(key=len)
	for node in nodes:
		if len(node) > 1:
			for j in range(1, len(node)):
				idx3 = find_node(tree['children'], node[j-1])
				idx2 = find_node(tree['children'][idx3]['children'], node[j])
				if idx2 > -1:
					tree['children'][idx3]['n_of_conversations'] += 1
					tree['children'][idx3]['children'][idx2]['n_of_conversations'] += 1
				else:
					idx3 = find_node(tree['children'], node[j])
					tree['children'][idx3]['n_of_conversations'] += 1	
		else:
			idx = find_node(tree['children'], node[0])
			tree['children'][idx]['n_of_conversations'] += 1

	tree2 = {'root':'root', 'children':[], 'n_of_conversations': 0, 'name':'root'}
	for i in tree['children']:
		if i['n_of_conversations'] > 0:
			tree2['n_of_conversations'] += i['n_of_conversations']
			tree2['children'].append(i)
		
	return tree2


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

