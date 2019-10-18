/**
 * Graph code mostly in sigma.js for the visualization
 */
import * as d3 from 'd3';

/**
 * Create a graph for d3
 *
 * @param el: a DOM element
 * @param data: Object, the data for the visualization, keys: "nodes" and "edges", each with
 *              an array
 * @param config: config for the visualization like width and height
 * @param handle_viz_events: function to pass visualization events back to react.

 */
export function create_graph(el, data, config, handle_viz_events) {
    let width = config.width;
    let height = config.height;

    const color = d3.scaleSequential(d3.interpolateBlues);
    let max_weight = 0;
    data.nodes.forEach(function(d){
        if (d.weight > max_weight){
            max_weight = d.weight;
        }
    });

    // label = floating names
    const label = {
        'nodes': [],
        'links': []
    };

    //adds nodes to label, push nodes twice = make 2 edges between nodes, make link stronger
    data.nodes.forEach(function(d, i) {
        label.nodes.push({node: d});
        label.nodes.push({node: d});
        label.links.push({
            source: i * 2,
            target: i * 2 + 1
        });
    });

    // defines forces between labels and nodes
    const labelLayout = d3.forceSimulation(label.nodes)
        .force("charge", d3.forceManyBody().strength(-50))
        .force("link", d3.forceLink(label.links).distance(0).strength(2));

    // defines the set up for the nodes themselves, charges are for the nodes
    const graphLayout = d3.forceSimulation(data.nodes)
        .force("charge", d3.forceManyBody().strength(-5000))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("x", d3.forceX(width / 2).strength(1))
        .force("y", d3.forceY(height / 2).strength(1))
        .force("link", d3.forceLink(data.links).id(function(d) {return d.name; }).distance(50)
            .strength(1))
        .on("tick", ticked);

    let adjlist = {};

    data.links.forEach(function(d) {
        adjlist[d.source.index + "-" + d.target.index] = true;
        adjlist[d.target.index + "-" + d.source.index] = true;
    });

    function neigh(a, b) {
        return a === b || adjlist[a + "-" + b];
    }

    const el_dom = d3.select(el);
    const svg = el_dom.append('svg').attr("width", width).attr("height", height);
    const container = svg.append("g");

    svg.call(
        d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", function() { container.attr("transform", d3.event.transform); })
    );

    const link = container.append("g").attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter()
        .append("line")
        .attr("stroke", "#aaa")
        .attr("stroke-width", "1px");

    const node = container.append("g").attr("class", "nodes")
        .selectAll("g")
        .data(data.nodes)
        .enter()
        .append("circle")
        .attr("r", function (d) {return Math.max(Math.pow(d.weight, 1/4), 5);})
        .attr("fill", function(d) { return color(0.5 + (Math.pow(d.weight/max_weight, 1/2))/2); });

    node.on("mouseover", focus).on("mouseout", unfocus);

    node.call(
        d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended)



    );

    const labelNode = container.append("g").attr("class", "labelNodes")
        .selectAll("text")
        .data(label.nodes)
        .enter()
        // .append("rect")
        // .attr("width", 20)
        // .attr("height", 10)
        // .style("fill", "#FFFFFF")
        // .style("stroke", "#0000FF")
        // .style("fill-opacity", 0.1)
        // .style("stroke-opacity", 0.9)
        .append("text")
        .text(function(d, i) { return i % 2 === 0 ? "" : d.node.name; })
        //.attr("class", "labelNode")
        .style("fill", "#555")
        .style("font-family", "Arial")
        .style("font-size", 12)
        .style("pointer-events", "none"); // to prevent mouseover/drag capture

    node.on("mouseover", focus)
        .on("mouseout", unfocus)
        .on("click", (node_data,_i) => handle_viz_events('click', node_data));

    function ticked() {

        node.call(updateNode);
        link.call(updateLink);

        labelLayout.alphaTarget(0.3).restart();
        labelNode.each(function(d, i) {
            if(i % 2 === 0) {
                d.x = d.node.x;
                d.y = d.node.y;
            } else {
                console.log(this);
                console.log(typeof this);
                const b = this.getBBox();

                const diffX = d.x - d.node.x;
                const diffY = d.y - d.node.y;

                const dist = Math.sqrt(diffX * diffX + diffY * diffY);

                let shiftX = b.width * (diffX - dist) / (dist * 2);
                shiftX = Math.max(-b.width, Math.min(0, shiftX));
                const shiftY = 16;
                this.setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
            }
        });
        labelNode.call(updateNode);

    }

    function fixna(val) {
        if (isFinite(val)) {return val}
        return 0;
    }

    function focus() {
        const index = d3.select(d3.event.target).datum().index;
        node.style("opacity", function(o) {
            return neigh(index, o.index) ? 1 : 0.1;
        });
        labelNode.attr("display", function(o) {
            return neigh(index, o.node.index) ? "block": "none";
        });
        link.style("opacity", function(o) {
            return o.source.index === index || o.target.index === index ? 1 : 0.1;
        });
    }

    function unfocus() {
        labelNode.attr("display", "block");
        node.style("opacity", 1);
        link.style("opacity", 1);
    }

    function updateLink(link) {
        link.attr("x1", function(d) { return fixna(d.source.x); })
            .attr("y1", function(d) { return fixna(d.source.y); })
            .attr("x2", function(d) { return fixna(d.target.x); })
            .attr("y2", function(d) { return fixna(d.target.y); });
    }

    function updateNode(node) {
        node.attr("transform", function(d) {
            return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
        });
    }

    function dragstarted(d) {
        d3.event.sourceEvent.stopPropagation();
        if (!d3.event.active) {graphLayout.alphaTarget(0.3).restart();}
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
        fix_nodes(d);
    }

    // Preventing other nodes from moving while dragging one node
    function fix_nodes(this_node) {
        node.each(function(d){
            if (this_node != d){
                d.fx = d.x;
                d.fy = d.y;
            }
        });
    }

    function dragended(d) {
        if (!d3.event.active) {graphLayout.alphaTarget(0);}
        // Set the dragged node equal to the original x and y positions
        d.fx = d.x;
        d.fy = d.y;
    }

}

// export function create_graph(el, data, config, handle_viz_events) {
//     d3.select(el)
//         .append('svg')
//         .attr('width', config.width)
//         .attr('height', config.height)
//         .selectAll('rect')
//         .data(data['nodes'])
//         .enter()
//         .append('rect')
//         .attr('x', (d, _i) => _i * 10)
//         .attr('y', (d) => config.height - d.docs / 25)
//         .attr('width', 9)
//         .attr('height', (d) => d.docs / 25)
//         .attr('fill', config.color)
//         .on('mouseover', (node_data,_i) => handle_viz_events('mouseover', node_data))
//         .on('mouseout',  (node_data,_i) => handle_viz_events('mouseout', node_data))
//         .on('click', (node_data, _i)    => handle_viz_events('click', node_data))
//     ;
// }


/**
 * Change the color of each of the rectangles in the graph, slowly.
 *
 * @param el: Node
 * @param data: object[]
 * @param config: object
 */
export function update_graph_color(el, data, config) {
    //D3 Code to update the chart
    // Re-compute the scales, and render the data points
    d3.select(el).selectAll('rect')
        .transition()
        .duration(1000)
        .style('fill', config.color)
}

/*
 * TODO:
 *   - destroy and recreate graph with new data
 *   - some kind of hooks to call different updates; e.g.,
 *     - filtering by topic
 *     -
 *
 */

