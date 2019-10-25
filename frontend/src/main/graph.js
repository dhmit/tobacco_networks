
/**
 * Graph code mostly in D3.js for the visualization
 */
import * as d3 from 'd3';

// D3 code is much more readable with non-standard indentation,
// so turning off standard eslint indent rules just for this file
/* eslint indent: 0 */

/**
 * Create a graph using d3
 *
 * @param el: DOM element where we'll render the graph
 * @param data: Object, the data for the visualization
 *              keys: "nodes" and "edges", each with an array of values
 * @param config: config for the visualization like width and height
 * @param handle_viz_events: function to pass visualization events back to react.
 */
export function create_graph(el, data, config, handle_viz_events) {
    const graph_width = config.width;
    const graph_height = config.height;

    // Initialize the force simulation - see https://github.com/d3/d3-force
    // This creates the x and y values for the data, based on relationships here
    // n.b. this doesn't actually render the sim - we do that below
    // by adding nodes to the svg and updating their position in render_simulation
    const force_link = d3.forceLink(data.links)
                         .id((d) => d.name)  // which data field to use as id for links
                         .distance(50)
                         .strength(1);
    const graph_x_center = graph_width / 2;
    const graph_y_center = graph_height / 2;

    const force_simulation = d3.forceSimulation(data.nodes)
        .force("link", force_link)
        .force("charge", d3.forceManyBody().strength(-5000))
        .force("center", d3.forceCenter(graph_x_center, graph_y_center))
        .force("x", d3.forceX(graph_x_center).strength(1))
        .force("y", d3.forceY(graph_y_center).strength(1))
        .on("tick", render_simulation);  // what to do when the sim updates


    // Setup the SVG that we're going to draw the graph into
    const svg = d3.select(el)
        .append('svg')
            .attr("width", graph_width)
            .attr("height", graph_height);


    // Create links
    const links = svg
        .append("g")
            .attr("id", "graph_links")
        .selectAll("line")
            .data(data.links)
        .enter()
            .append("line")
            .attr("stroke", "#aaa")
            .attr("stroke-width", "1px");


    // node is an SVG g -- will contain circle + label
    const nodes = svg
        .append("g")
            .attr("id", "graph_nodes")
        .selectAll("g")
            .data(data.nodes)
        .enter()
            .append("g")
                .attr('id', (d) => d.name);  // TODO: replace this with a fixed key rather than name

    nodes  // bind event handlers for nodes
        .call(
            d3.drag()
                .on("start", drag_started)
                .on("drag", dragged)
                .on("end", drag_ended)
        )
        .on("mouseover", focus_node)
        .on("mouseout", unfocus_node)
        .on("click", (d, _i) => handle_viz_events('click', d));

    // Setup circle helper funcs
    // Find max weight of all nodes, for scaling
    // TODO: replace this with a scale with domain/range
    let max_weight = 0;
    for (const node of data.nodes) {
        if (node.weight > max_weight) {
            max_weight = node.weight;
        }
    }
    const circle_color_scale = d3.scaleSequential(d3.interpolateBlues)
    const calc_circle_color = (d) => {
        const floor = .5;
        return circle_color_scale(floor + .5 * Math.pow(d.weight / max_weight, .5));
    };
    const calc_circle_radius = (d) => Math.max(Math.pow(d.weight, 1/3), 5);

    // Actually setup circles
    nodes
        .append("circle")
            .attr("r", (d) => calc_circle_radius(d))
            .attr("fill", (d) => calc_circle_color(d))

    // Setup labels
    const calc_label_pos = (_d, _i, _nodes) => {
        // const label = nodes[i];
        // const b = label.getBBox();  // bounding box of the label
        // TODO: adjust position of the label based on radius of the circle
        const shiftX = 10;
        const shiftY = 5;
        return `translate(${shiftX}, ${shiftY})`;
    };
    nodes
        .append("text")
            .text((d) => d.name)
            .style("fill", "#555")
            .style("font-family", "Arial")
            .style("font-size", 12)
            .attr("transform", (d, i, n) => calc_label_pos(d, i, n));

    /*
     * Event handlers
     */
    // Update the position of all svg elements according to the force sim
    // This function is called whenever the simulation updates
    function render_simulation() {
        // Update node positions
        nodes.attr("transform", (d) => `translate(${d.x}, ${d.y})` );

        // Update link positions
        links.attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);
    }

    function drag_started(d) {
        d3.event.sourceEvent.stopPropagation();
        if (!d3.event.active) {force_simulation.alphaTarget(0.3).restart();}
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function drag_ended(d) {
        if (!d3.event.active) {force_simulation.alphaTarget(0);}
        d.fx = null;
        d.fy = null;
    }

    // Setup adjacencies (maybe refactor this...)
    const adjacent_nodes = {};
    for (const link of data.links) {
        adjacent_nodes[link.source.index + "-" + link.target.index] = true;
        adjacent_nodes[link.target.index + "-" + link.source.index] = true;
    }
    function neigh(a, b) {
        return a === b || adjacent_nodes[a + "-" + b];
    }

    function focus_node() {
        const node = d3.select(d3.event.target);
        const index = node.datum().index;
        nodes.style("opacity", function(o) {
            return neigh(index, o.index) ? 1 : 0;
        });
        links.style("opacity", function(o) {
            return o.source.index === index || o.target.index === index ? 1 : 0;
        });
    }

    function unfocus_node() {
        nodes.style("opacity", 1);
        links.style("opacity", 1);
    }
}


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
export function update_graph_size(el, data, config) {
    // d3.select(el).selectAll('rect')
    //     .transition()
    //     .duration(1000)
    //     .style('fill', config.color)

    d3.select(el)
        .append('svg')
            .attr("width", config.width)
            .attr("height", config.height);
}
