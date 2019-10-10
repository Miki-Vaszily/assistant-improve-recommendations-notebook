class NodePath:

	def __init__(self, nodes):
		self.nodes = nodes
	
	def get_final_output_text(self):
		from utils import get_output_text
		return get_output_text(self.nodes[-1])
