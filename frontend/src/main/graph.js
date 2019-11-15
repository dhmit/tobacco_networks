
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
    let graph_width = config.width;
    let graph_height = config.height;

    // Initialize the force simulation - see https://github.com/d3/d3-force
    // This creates the x and y values for the data, based on relationships here
    // n.b. this doesn't actually render the sim - we do that below
    // by adding nodes to the svg and updating their position in render_simulation
    const force_link = d3.forceLink(data.links)
                         .id((d) => d.name)  // which data field to use as id for links
                         .distance(50);
    const graph_x_center = graph_width / 2;
    const graph_y_center = graph_height / 2;

    let centers = {"Phillip Morris International": [graph_width * .2, graph_height * .2],
                     "British American Tobacco": [graph_width * .8, graph_height * .2],
                     "Imperial Tobacco": [graph_width * .2, graph_height * .8],
                     "Japan Tobacco": [graph_width*.8, graph_height*.8]};

    const force_simulation = d3.forceSimulation(data.nodes)
    function runForceSim() {
        force_simulation.force("link", force_link)
        .force("charge", d3.forceManyBody().strength(-1000))
        .force("center", d3.forceCenter(graph_x_center, graph_y_center))
        .force('collision', d3.forceCollide().radius(30))
        .force('x', d3.forceX().x(function(d) {
            return centers[d.affiliation][0];
        }).strength(5))
        .force('y', d3.forceY().y(function(d) {
            return centers[d.affiliation][1];
        }).strength(5))
        .on("tick", render_simulation);  // what to do when the sim updates
    }
    runForceSim();

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
            .attr("class", "graph_link")
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
            .attr("class", "graph_node")
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
    let circle_color_scale;
    const calc_circle_color = (d) => {
        const floor = .5;
        if (d.affiliation === "Phillip Morris International") {
            circle_color_scale  = d3.scaleSequential(d3.interpolateBlues)
        } else if (d.affiliation === "British American Tobacco") {
            circle_color_scale  = d3.scaleSequential(d3.interpolateReds)
        } else if(d.affiliation === "Imperial Tobacco") {
            circle_color_scale  = d3.scaleSequential(d3.interpolateGreens)
        } else {
            circle_color_scale  = d3.scaleSequential(d3.interpolateGreys)
        }
        return circle_color_scale(floor + .5 * Math.pow(d.weight / max_weight, .5));
    };
    const calc_circle_radius = (d) => Math.max(Math.pow(d.weight, 1/3), 5);

    // Actually setup circles
    nodes
        .append("circle")
            .attr("r", (d) => calc_circle_radius(d))
            .attr("fill", (d) => calc_circle_color(d))

    // Setup labels
    const calc_label_pos = (d, i, nodes) => {
        const label = nodes[i];
        const r = calc_circle_radius(d);
        const h = label.getBBox().height;  // bounding box of the label
        const w = label.getBBox().width;
        // TODO: adjust position of the label based on radius of the circle
        const shiftX = -w/2;
        const shiftY = -h/2-r;
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
        nodes.attr("transform", (d) => { return `translate(${d.x}, ${d.y})`} );

        // Update link positions
        links.attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);
    }

    function drag_started(d) {
        nodes.on("mouseover", () => {}).on("mouseout", () => {});
        d3.event.sourceEvent.stopPropagation();
        if (!d3.event.active) {force_simulation.alphaTarget(0.3).restart();}
        d.fx = d.x;
        d.fy = d.y;
    }
    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;

        // fix_nodes(d);
    }

    // Preventing other nodes from moving while dragging one node
    // function fix_nodes(this_node) {
    //     nodes.each(
    //         function(node){
    //         if (this_node != node){
    //             node.fx = node.x;
    //             node.fy = node.y;
    //          }
    //      });
    //  }

    function drag_ended(d) {
        if (!d3.event.active) {force_simulation.alphaTarget(0);}
        d.fx = d.x;
        d.fy = d.y;
        nodes.on("mouseover", focus_node).on("mouseout", unfocus_node);
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

        // TODO: Fix this to pass in the node name
        get_information(data, "DUNN,WL");
    }

    function unfocus_node() {
        nodes.style("opacity", 1);
        links.style("opacity", 1);
    }

    d3.select(window).on("resize", resize);

    function resize() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        centers = {"Phillip Morris International": [width * .2, height * .2],
                     "British American Tobacco": [width * .8, height * .2],
                     "Imperial Tobacco": [width * .2, height * .8],
                     "Japan Tobacco": [width*.8, height*.8]};
        force_simulation.alphaTarget(0.3).restart();
        runForceSim();
        svg.attr("width", width).attr("height", height);
        console.log(width,height);
        force_simulation.force("center", d3.forceCenter(width / 2,height / 2)).restart();
        render_simulation(); // not sure if this makes a difference
    }
}

/**
 * Change the color of each of the rectangles in the graph, slowly.
 *
 * @param el: Node
 * @param data: object[]
 * @param config: object
 */

/**
 * Returns information of the given id
 *
 * @param data: data
 * @param name: String
 */
// TODO: Display information somewhere
export function get_information(data, name){
    name = name.toUpperCase();
    const data_nodes = data["nodes"];
    let name_info = {};

    for(const indx in data_nodes){
        const current_name = data_nodes[indx];
        if (current_name["name"]  == name){
            name_info = current_name;
        }
    }

    return name_info;
}

/**
 * Updates visualization according to what the user searches
 *
 * @param data: data
 * @param name: String
 */
export function update_focused_node(el, data, config) {
        const name = config.search_person_name.toUpperCase();
        console.log("entered update focused node")
        // then for each node check if node is a neighbor; if yes set opacity to 1, if not set to 0
        const neigh = []
        const data_edges = data["links"];

        for (const indx in data_edges){
            const other_name_1 = data_edges[indx]["node1"].toUpperCase();
            const other_name_2 = data_edges[indx]["node2"].toUpperCase();
            if( other_name_1 != other_name_2) {
                if (other_name_1 == name) {
                    neigh.push(other_name_2);
                }
                else if(other_name_2 == name) {
                    neigh.push(other_name_1);
                }
            }
        }
        // TODO: Fix selector

        // need to fix the selector
        const node = d3.select("#"+name);
        console.log(node);

        /*
        console.log(node);
        const index = node.datum().index;
        const nodes = d3.selectAll(".graph_node");

        nodes.style("opacity", function(o) {
            if ( o in neigh) {
                return o.source.index ? 1:0;
            }
        });
        const links = d3.selectAll(".graph_link");
        links.style("opacity", function(o) {
            return o.source.index === index || o.target.index === index ? 1 : 0;
        });
        */
}
