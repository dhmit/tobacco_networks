
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
    const adj_data = data["adjacent_nodes"];
    const graph_width = config.width;
    const graph_height = config.height;

    // Initialize the force simulation - see https://github.com/d3/d3-force
    // This creates the x and y values for the data, based on relationships here
    // n.b. this doesn't actually render the sim - we do that below
    // by adding nodes to the svg and updating their position in render_simulation


    let force_simulation = initialize_force_sim(config, data);

    // Setup the SVG that we're going to draw the graph into
    const svg = d3.select(el)
        .append('svg')
            .attr("width", graph_width)
            .attr("height", graph_height)
            .attr("id", "svg_id");

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
            .attr("fill", (d) => calc_circle_color(d));

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
            .attr("transform", (d, i, n) => calc_label_pos(d, i, n))
                .style("pointer-events", "none");
    console.log(nodes)
    /*
     * Event handlers
     */
    // Update the position of all svg elements according to the force sim
    // This function is called whenever the simulation updates
    // eslint-disable-next-line no-unused-vars
    function render_simulation() {
        // Update node positions
        nodes.attr("transform", (d) => { return `translate(${d.x}, ${d.y})`} );

        // Update link positions
        links.attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);
        config.nodes = nodes;
        config.links = links;
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
        d.has_been_dragged = true;
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
        d.fx = null;
        d.fy = null;
        d.x_grav = d.x;
        d.y_grav = d.y;
        d.has_been_dragged = true;
        force_sim();
        nodes.on("mouseover", focus_node).on("mouseout", unfocus_node);
    }

    function focus_node() {
        const node = d3.select(d3.event.target);
        const name = node["_groups"][0][0]["__data__"]["name"];

        nodes.style("opacity", function(o) {
            const other_name = o.name;
                if (other_name + "-" + name in adj_data) {
                    return 1;
                } else if (other_name === name) {
                    return 1;
                }
                return 0;
        });

        links.style("opacity", function(o) {
            const source = o.source.name;
            const target = o.target.name;
            if (name === source || name === target) {
                return 1;
            }
            return 0;
        });
        config.nodes = nodes;
        config.links = links;
        // TODO: Fix this to pass in the node name
        get_information(data, "DUNN,WL");
    }

    function unfocus_node() {
        nodes.style("opacity", 1);
        links.style("opacity", 1);
        config.nodes = nodes;
        config.links = links;
    }
    function resize() {
        const width = window.innerWidth;
        const height = window.innerHeight;

        svg.attr("width", width).attr("height", height);
        config.width = width;
        config.height = height;
        let force_simulation = initialize_force_sim(config, data);
        force_simulation.alphaTarget(0.3).restart();
        force_simulation.alphaTarget(0);
    }

    function force_sim(){
        let centers
        if (config.cluster_nodes) {
            centers = {
                "Phillip Morris International": [graph_width * .2, graph_height * .2],
                "British American Tobacco": [graph_width * .8, graph_height * .2],
                "Imperial Tobacco": [graph_width * .2, graph_height * .8],
                "Japan Tobacco": [graph_width * .8, graph_height * .8]
                };
        } else {
            centers = {
                "Phillip Morris International": [graph_width/2, graph_height/2],
                "British American Tobacco": [graph_width/2, graph_height/2],
                "Imperial Tobacco": [graph_width/2, graph_height/2],
                "Japan Tobacco": [graph_width/2, graph_height/2]
            };
        }

        const force_x_pos = (d) => {
            if (d.has_been_dragged){
                return d.x_grav;
            } else {
                return centers[d.affiliation][0];
            }
        }
        const force_y_pos = (d) => {
            if (d.has_been_dragged){
                return d.y_grav;
            } else {
                return centers[d.affiliation][1];
            }
        }
        const cluster_strength = (d) => {
            if (d.has_been_dragged){
                return 5;
            } else {
                return 3;
            }
        }

    let force_simulation = d3.forceSimulation(data.nodes);
    force_simulation
        .force("charge", d3.forceManyBody())
        .force('collision', d3.forceCollide().radius(30))
        .force('x', d3.forceX().x((d) => force_x_pos(d)).strength(cluster_strength))
        .force('y', d3.forceY().y((d) => force_y_pos(d)).strength(cluster_strength))
        .on("tick", render_simulation);  // what to do when the sim updates
    }

    d3.select(window).on("resize", resize);

    config.svg = svg;
    config.nodes = nodes;
    config.links = links;
}

function initialize_force_sim(config, data) {
    const graph_width = config.width;
    const graph_height = config.height;

    let centers;
    let link_strength;
    let cluster_strength;
    let charge_strength;
    let radius_distance;
    if (config.cluster_nodes) {
        centers = {
            "Phillip Morris International": [graph_width * .2, graph_height * .2],
            "British American Tobacco": [graph_width * .8, graph_height * .2],
            "Imperial Tobacco": [graph_width * .2, graph_height * .8],
            "Japan Tobacco": [graph_width * .8, graph_height * .8]
        };
        link_strength = 0;
        charge_strength = -1000;
        cluster_strength = 5;
        radius_distance = 30;
    } else {
        centers = {
            "Phillip Morris International": [graph_width/2, graph_height/2],
            "British American Tobacco": [graph_width/2, graph_height/2],
            "Imperial Tobacco": [graph_width/2, graph_height/2],
            "Japan Tobacco": [graph_width/2, graph_height/2]
        };
        link_strength = 1;
        charge_strength = -5000;
        cluster_strength = 3;
        radius_distance = 0;
    }
    const force_link = d3.forceLink(data.links)
                         .id((d) => d.name)  // which data field to use as id for links
                         .distance(50)
                         .strength(link_strength);

    const force_x_pos = (d) => {
        console.log(d.has_been_dragged);
        return centers[d.affiliation][0];
    }

    let force_simulation = d3.forceSimulation(data.nodes);
    force_simulation.force("link", force_link)
        .force("charge", d3.forceManyBody().strength(charge_strength))
        .force("center", d3.forceCenter(graph_width/2, graph_height/2))
        .force('collision', d3.forceCollide().radius(radius_distance))
        .force('x', d3.forceX()
                        .x((d) => force_x_pos(d))
                        .strength(cluster_strength))
        .force('y', d3.forceY().y(function(d) {
            return centers[d.affiliation][1];
        }).strength(cluster_strength))
        .on("tick", render_simulation);  // what to do when the sim updates

    function render_simulation() {
        // Update node positions
        config.nodes.attr("transform", (d) => { return `translate(${d.x}, ${d.y})`} );

        // Update link positions
        config.links.attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);
    }

    function resize() {
        const svg = d3.select("svg_id")
        console.log("RESIZING", config.width, config.height);
        const width = window.innerWidth;
        const height = window.innerHeight;
        svg.attr("width", width).attr("height", height);
        config.width = width;
        config.height = height;
        let force_simulation = initialize_force_sim(config, data);
        force_simulation.alphaTarget(0.3).restart();
        force_simulation.alphaTarget(0);
    }
    d3.select(window).on("resize", resize);
    return force_simulation;
}


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
        if (current_name["name"]  === name){
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
export function update_graph(el, data, config, action) {
    if (action === 'focus') {
        update_focused_node(el, data, config);
    } else if (action === "cluster_nodes") {
        initialize_force_sim(config, data);
    } else {
        //function update_unfocus_node (el, data, config) {
        const svg = d3.select(el);
        svg.selectAll(".graph_node").style("opacity", 1);
        svg.selectAll(".graph_link").style("opacity", 1);
    }

    function update_focused_node(el, data, config) {
        const name = config.search_person_name.toUpperCase();
        const svg = d3.select(el);
        const adj_data = data["adjacent_nodes"];
        svg.selectAll(".graph_node")
            .style("opacity", function (o) {
                const other_name = o.name;
                if (other_name + "-" + name in adj_data) {
                    return 1;
                } else if (other_name === name) {
                    return 1;
                }
                return 0;
            });
        svg.selectAll(".graph_link")
            .style("opacity", function (o) {
                const source = o.source.name;
                const target = o.target.name;

                if (name === source || name === target) {
                    return 1;
                }
                return 0;
            });
    }

}
