// Set the dimensions and margins of the diagram

var margin = {top: 0, right: 40, bottom: 20, left: 0},

    width = 1300 - margin.left - margin.right,

    height = 1300 - margin.top - margin.bottom;

var svg = d3.select("#graph").append("svg").attr("width", width + margin.right + margin.left)
										 .attr("height", height + margin.top + margin.bottom).append("g")
										 .attr("transform", "translate(" + 50 + ", " + 30  + ")");

var i = 0, duration = 550, root;
var treemap = d3.tree().size([height-100, width-100])

d3.json("tree.json", function(error, treeData) {
	if (error) throw error;
	root = d3.hierarchy(treeData, function(d) { return d.children; });
	root.x0 = 0; 
	root.y0 = 0;

	// Collapse after the second level
    root.children.forEach(collapse);
	update(root);	
	});

  function collapse(d) {
     if(d.children) {
       d._children = d.children
       d._children.forEach(collapse)
       d.children = null
	 }
   }

  function update(source) {
  // Assigns the x and y position for the nodes
  var treeData = treemap(root);
  // Compute the new tree layout.
  var nodes = treeData.descendants(),
      links = treeData.descendants().slice(1);

  // Normalize for fixed-depth.

  nodes.forEach(function(d){ d.y = d.depth * 130});


  // ****************** Nodes section ***************************
               
  // Update the nodes...
  var node = svg.selectAll('g.node')
      .data(nodes, function(d) {return d.id || (d.id = ++i); });
  // Enter any new modes at the parent's previous position.
  var nodeEnter = node.enter().append('g')
   	 .attr("transform", function(d) {
		if(d.data.name == "root") {
			d.x = 2;
			d.y = 0;
			d.data['shape'] = 'circle';
        	return "translate(" + 0 + "," + 2 + ")";
		}    
		if(d.data.type == "standard"){
			d.data['shape'] = 'circle';
		}else {
			d.data['shape'] = 'rect';
		}    
             
    }).attr('class', function(d) {
		return d.data.shape + " node";
	
	})
    .on('click', click);


    
  // Add Circle for the nodes
   d3.selectAll('.circle').append("circle")
		.attr('r', 10)
		.attr('class', '_circle')
		.style("fill", function(d) {
			if(d.data.n_of_conversations > 1000) {
				return "#f60c0c";
			}else if(d.data.n_of_conversations > 500) {
				return "34a507";
			}else if(d.data.n_of_conversations > 100) {
				return "f6e10c";
			}else{
				return "lightsteelblue";
			}
		});
	
	d3.selectAll('.rect').append("rect")
		.attr('width', 18)
		.attr('height', 18)
		.attr('class', '_rect')
		.style("fill", function(d) {
			if(d.data.n_of_conversations > 1000) {
       			return "#f60c0c";
			}else if(d.data.n_of_conversations > 500) {
				return "34a507";
			}else if(d.data.n_of_conversations > 100) {
				return "f6e10c";
			}else{
				return "lightsteelblue";
     		}
		});

  // Add labels for the nodes
  nodeEnter.append('text')
      .attr("dy", ".30em")
      .attr("x", function(d) {
		if(d.data.shape == 'circle') {
			if(d.data.root) {
				return 40;
			}
			return 30;
		}
      })
      .attr("text-anchor", function(d) {
			if(d.data.shape == 'circle') {
				return "start";
			}
      })
      .text(function(d) {
		if(d.data.shape == 'circle') {
			if(d.data.name) {
				if(d.data.name.length > 15) {
					return "[" + d.data.n_of_conversations + "] " + d.data.name.substring(0,13) + "...";
				}else {
					return "[" + d.data.n_of_conversations + "] " + d.data.name;
				}
		    }
		}});

  nodeEnter.append('text')
      .attr("dy", "1em")
      .attr("x", function(d) {
		if(d.data.shape == 'rect') {
			return 40;
		}
      })
      .attr("text-anchor", function(d) {
			if(d.data.shape == 'rect') {
				return "start";
			}
      })
      .text(function(d) {
		if(d.data.shape == 'rect') {
			if(d.data.name) {
				if(d.data.name.length > 15) {
					return "[" + d.data.n_of_conversations + "] " + d.data.name.substring(0,13) + "...";
				}else {
					return "[" + d.data.n_of_conversations + "] " + d.data.name;
				}
		    }
		}});

	nodeEnter.append('text')
		.attr("dy", ".35em")
		.attr("dx", "-.25em")
		.text(function(d) {
			if(d.data.shape == 'circle') {
				return d.children || d._children ? "+" : "";
			}
		});
	nodeEnter.append('text')
		.attr("dy", "1em")
		.attr("dx", ".45em")
		.text(function(d) {
			if(d.data.shape == 'rect') {
				return d.children || d._children ? "+" : "";
			}
		});


  // UPDATE
  var nodeUpdate = nodeEnter.merge(node);
  // Transition to the proper position for the node
  nodeUpdate.transition()
    .duration(duration)
    .attr("transform", function(d) {
		if(d.parent) {
			if(d.data.shape == 'circle'){
				return "translate(" + d.y + "," + d.x + ")";
			}else {
				return "translate(" + (d.y-9) + "," + (d.x-10) + ")";
			}

		}else {
	        d.x = 2;
			d.y = 0;
        	return "translate(" + 0 + "," + 2 + ")";
		}
     });
  // Update the node attributes and style
	nodeUpdate.select('.circle.node')
        .attr('r', 10)
        .style("fill", function(d) {
		if(d.data.n_of_conversations > 1000) {
		  	return "#f60c0c";
		  }else if(d.data.n_of_conversations > 500) {
		  	return "#34a507";
		  }else if(d.data.n_of_conversations > 100) {
		  	return "#f6e10c";
		  }else {	 	 	
          	return "lightsteelblue";
		  }
   })
   .attr('cursor', 'pointer');

  nodeUpdate.select('.rect.node')
     .attr('width', 18)
	 .attr('height', 18)
     .style("fill", function(d) {
	  if(d.data.n_of_conversations > 1000) {
		  	return "#f60c0c";
	  }else if(d.data.n_of_conversations > 500) {
		  	return "#34a507";
	  }else if(d.data.n_of_conversations > 100) {
	    	return "#f6e10c";
	  }else {	 	 	
          	return "lightsteelblue";
	  }
   })
   .attr('cursor', 'pointer');
    
	nodeUpdate.append('text')
		.attr("dy", ".35em")
		.attr("dx", "-.25em")
		.text(function(d) {
			if(d.data.shape == 'circle') {
				return d.children || d._children ? "+" : "";
				
			}
		});
	nodeUpdate.append('text')
		.attr("dy", "1em")
		.attr("dx", ".45em")
		.text(function(d) {
			if(d.data.shape == 'rect') {
				return d.children || d._children ? "+" : "";
			}
		});

  // Remove any exiting nodes
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) {
		  if(source.name == "root") {
 			source.x = 2;
		    source.y = 0;
		  }
          return "translate(" + source.y + "," + source.x + ")";
      })
      .remove();

  // On exit reduce the node circles size to 0

  // On exit reduce the opacity of text labels
  nodeExit.select('text')
    .style('fill-opacity', 1e-6);

  // ****************** links section ***************************
  	
  // Update the links...
  var link = svg.selectAll('path.link')
      .data(links, function(d) { 
	  return d.id; 
});
  // Enter any new links at the parent's previous position.
  var linkEnter = link.enter().insert('path', "g")
      .attr("class", "link")
      .attr('d', function(d){
		if(d.parent.name == "root") {
			d.parent.x = 2;
			d.parent.y = 0;
		}
        var o = {x: source.x0, y: source.y0}
        return diagonal(o, o)
      });

  // UPDATE
  var linkUpdate = linkEnter.merge(link);
  // Transition back to the parent element position
  linkUpdate.transition()
      .duration(duration)
      .attr('d', function(d){ 
		if(d.parent.name == "root") {
			d.parent.x = 2;
			d.parent.y = 0;
		}
		return diagonal(d, d.parent) 
		});

  // Remove any exiting links
  var linkExit = link.exit().transition()
      .duration(duration)
      .attr('d', function(d) {
		if(d.parent.name == "root") {
			d.parent.x = 2;
			d.parent.y = 0;
		}
        var o = {x: source.x, y: source.y}
        return diagonal(o, o);
      })
      .remove();
  // Store the old positions for transition.
  nodes.forEach(function(d){
    d.x0 = d.x;
    d.y0 = d.y;
  });



  // Creates a curved (diagonal) path from parent to the child nodes
  function diagonal(s, d) {
    var path = `M ${s.y} ${s.x}
            C ${(s.y + d.y) / 2} ${s.x},
              ${(s.y + d.y) / 2} ${d.x},
              ${d.y} ${d.x}`
   
    return path
  }
  // Toggle children on click.
  function click(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }

    update(d);
  }
}

