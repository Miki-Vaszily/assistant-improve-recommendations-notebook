import numpy as np
import json
import os
import traceback
from typing import List, Dict, Tuple, Optional
from node_path import NodePath
import glob

def load_raw_workspace(workspace_path):
    with open(workspace_path, "r") as fl:
        return json.load(fl)

def load_logs(log_path):
	with open(log_path, "r") as fl:
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
	if 'parent' in node and 'parent' in node['parent'] and node['parent']['parent'] == 'root':
		return 'root'
	if 'parent' in node and node['parent'] == 'root':
		return 'root'

	if "parent" in node:
		print(node)
		return nodes[node['parent']]
	else:
		#return node['root']
		return "root"

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
#			print(node)
			node['children'].append(get_graph_children(workspace, node))
			result.append(node)

	if len(result) > 0:
		result = helper_function(workspace, result)
	return result


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



###################################################################
"""def set_data_root(workspace):
	parents_standard = []
	parents_response = []
	all_nodes = []
	for pos, node in enumerate(workspace['dialog_nodes']):
		if 'parent' not in node and node['type'] == "standard":
			parents_standard.append(node['dialog_node'])
		elif 'parent' not in node and node['type'] != "standard":
			parents_response.append(node['dialog_node'])
		elif 'parent' in node:
			all_nodes.append(node)	

	tmp = {}
	for i in parents_standard:
		for j in workspace['dialog_nodes']:
			if j['dialog_node'] == i and 'previous_sibling' not in j:
				tmp['first'] = i
			elif j['dialog_node'] == i:
				tmp[j['previous_sibling']] = j['dialog_node']

	tree = {'root':'root', 'type': 'standard', 'children': []}
	parents_standard_ = [tmp['first']]
	nd = tmp['first']
	del tmp['first']
	while len(tmp) > 0:
		parents_standard_.append(tmp[nd])
		del tmp[nd]
		nd = parents_standard_[-1]

	for nd in parents_standard_:
		for i in workspace['dialog_nodes']:
			if nd == i['dialog_node']:
				if 'title' in i:
					tree['children'].append({'name': i['title'], 'type': i['type'], 'conditions': i['conditions'], 'n_of_conversations': 0, 'dialog_node': i['dialog_node'], 'children': []})
				else:
					tree['children'].append({'name': i['conditions'], 'type': i['type'], 'dialog_node': i['dialog_node'], 'n_of_conversations': 0, 'children':[]})

	return tree
"""
"""def set_data(workspace, node):
	
	tmp = {}
	for i in node:
		nd = get_graph_children(workspace, node)
		if len(nd) == 0: return node
		for j in nd:
			if 'previous_sibling' not in j:
				tmp['first'] = j['dialog_node']
			else:
				tmp[j['previous_sibling']] = j['dialog_node']

	helper = [tmp['first']]	
	nd = tmp['first']
	del tmp['first']
	while len(tmp) > 0:
		helper.append(tmp[nd])
		del tmp[nd]
		nd = helper[-1]

	for i in helper:
		for nd in workspace['dialog_nodes']:
			if i == nd['dialog_node']:
				if 'title' in nd:
					node['children'].append({'name': nd['title'], 'conditions': nd['conditions'], 'type': nd['type'], 'dialog_node': nd['dialog_node'], 'n_of_conversations': 0, 'children': []})
				elif 'conditions' in nd:
					node['children'].append({'name': nd['conditions'], 'dialog_node': nd['dialog_node'], 'type': nd['type'], 'n_of_conversations': 0, 'children': []})
	return node

def is_root_child(root, node):

	for i in root['children']:
		if i['dialog_node'] == node['parent']:
			return True
	return False
"""
def helper_function(node):

	tmp = {}
	for i in node:
		if 'previous_sibling' not in i:
			tmp['first'] = i['dialog_node']
		else:
			tmp[i['previous_sibling']] = i['dialog_node']

	helper = [tmp['first']]	
	nd = tmp['first']
	del tmp['first']
	while len(tmp) > 0:
		helper.append(tmp[nd])
		del tmp[nd]
		nd = helper[-1]

	res = []
	for i in helper:
		for j in node:
			if i == j['dialog_node']:
				if 'name' in j:
					res.append({'name': j['name'], 'conditions': j['conditions'], 'type': j['type'], 'dialog_node': j['dialog_node'], 'n_of_conversations': j['n_of_conversations'], 'n_of_end_conversations': j['n_of_end_conversations'], 'children':[], 'parent':j['parent']})
				break
	
	return res

def helper(node, nodes):
	if node['dialog_node'] not in nodes:
		return node
	else:
		for i in nodes[node['dialog_node']]:
			node['children'].append(helper(i, nodes))
			
	return node
	

def clean_data(node):

	res = {'children': []}
	if 'title' in node and 'conditions' in node:
		res['name'] = node['title']
		res['type'] = node['type']
		res['conditions'] = node['conditions']
	elif 'conditions' in node:
		res['name'] = node['conditions']
		res['type'] = node['type']
		res['conditions'] = node['conditions']
	else:
		if node['type'] == "folder":
			res['name'] = node['title']
		elif node['type'] == "slot":
			res['name'] = node['variable']
		else:
			res['name'] = node['type']

		res['conditions'] = 'response_conditions'
		res['type'] = node['type']
		
	res['dialog_node'] = node['dialog_node']
	
	res['n_of_conversations'] = node['n_of_conversations']
	res['n_of_end_conversations'] = node['n_of_end_conversations']
	if 'parent' in node:
		res['parent'] = node['parent']
	else:
		res['parent'] = 'root' 		

	if 'previous_sibling' in node:
		res['previous_sibling'] = node['previous_sibling']


	if 'children' in node:
		for i in node['children']:
			if (type(i) != list ):
				res['children'].append(i)
				break

	return res

def create_tree(workspace):

	s = {}

	for i in workspace['dialog_nodes']:
		nd2 = clean_data(i)
		if nd2['parent'] not in s:
			s[nd2['parent']] = [nd2]
		else:
			s[nd2['parent']].append(nd2)
	for i in s:
		s[i] = helper_function(s[i])

	tree = {'name': 'root', 'type': 'standard', 'n_of_conversations': 0, 'children': s['root']}
	for i in tree['children']:
		i = helper(i, s)

	return tree

def compute_number_of_conversations(workspace, logs):

	data = workspace['dialog_nodes'].copy()
	nodes = []
	for i in data:
		nodes.append(i['dialog_node'])
		i['n_of_conversations'] = 0
		i['n_of_end_conversations'] = 0
	nodes = np.array(nodes)
	total_conv = 0
	
	for i in logs:
		lg = i['response']['output']['nodes_visited']	
		for visited in lg :
			a = np.where(nodes==visited)
			if len(a[0]) == 0: continue
			total_conv += 1
			if len(i['response']['output']['log_messages']) > 0 and i['response']['output']['log_messages'][0]['level'] == 'err':
				data[a[0][0]]['n_of_end_conversations'] += 1	
			else:
				data[a[0][0]]['n_of_conversations'] += 1

	return total_conv

def concatenate_logs(path):
	logs_week = []
	for filename in os.listdir(path):
		with open(path+filename, 'r') as fl:
			lg = json.load(fl)
			for i in lg['logs']:
				logs_week.append(i)

	return logs_week
