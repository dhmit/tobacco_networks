/**
 * Graph code mostly in D3.js for the visualization
 */
import * as d3 from 'd3';
import './graph.css';

import {update_node_degree_and_visibility} from "./node_degree_calculation";

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

    console.log(data);

    // Setup the SVG that we're going to draw the graph into
    const svg = d3.select(el)
        .append('svg')
            .attr("width", config.width)
            .attr("height", config.height)
            .attr("id", "graph_svg");

    // to calculate node degrees and visibility, we need the data-bindings, so we're creating them
    // here first, then we update the data with degree and visibility info, and then we use that
    // info to set the attributes of the visualization

    // Create links (they go to the background/bottom of the visualization
    const links = svg
        .append("g")
            .attr("id", "graph_links")
        .selectAll("line")
            .data(data.links)
        .enter()
            .append("line");

    // clusters are the affiliation groups, e.g. Philip Morris
    // each consists of a group with one text element.
    const clusters = svg
        .append("g")
            .attr("id", "graph_clusters")
        .selectAll("g")
            .data(Object.values(data.clusters))
        .enter()
            .append("g")
                .attr("id", (d) => `cluster_${d.name}`);

    // node is an SVG g -- will contain circle + label (a group with a rect and a text element)
    const nodes = svg
        .append("g")
            .attr("id", "graph_nodes")
        .selectAll("g")
            .data(data.nodes)
        .enter()
            .append("g")
            .attr("class", "graph_node")
            .attr('id', (d) => d.name);  // TODO: replace this with a fixed key rather than name

    // store data bindings and initialize force simulation
    let data_bindings = {
        'svg': svg,
        'nodes': nodes,
        'links': links,
        'clusters': clusters
    };

    // initializing the force simulation connects the links and edges, i.e. we can modify
    // node data through the links
    // before this step, link.source/target is a string.
    // after this step, it's a node and we can access its attributes e.g. with node.degree
    let force_simulation = initialize_force_sim(config, data, data_bindings);

    update_node_degree_and_visibility(data, config);

    // // Set link attributes
    // const link_width_scale_degree_1 = d3.scaleLinear()
    //     .domain([0, d3.max(data['links'], function(d) { return d.docs})])
    //     .range([2, 3]);
    // const link_width_scale_degree_2 = d3.scaleLinear()
    //     .domain([0, d3.max(data['links'], function(d) { return d.docs})])
    //     .range([0.5, 2]);
    // links
    //     .attr("class", (d) => `graph_link degree_${d.degree}`)
    //     .attr("stroke-width", (d) => {
    //         if (d.degree === 1){
    //             return link_width_scale_degree_1(d.docs);
    //         } else {
    //             return link_width_scale_degree_2(d.docs);
    //         }
    //     })
    //     .attr('visibility', (d) => d.visibility);

    // add node circle and labels
    const max_docs = d3.max(data['nodes'], function(d) { return d.docs; });
    const node_size_scale_degree_1 = d3.scaleLinear()
        .domain([0, max_docs])
        .range([20, config.width * config.height / 60000]);
    const node_size_scale_degree_2 = d3.scaleLinear()
        .domain([0, max_docs])
        .range([5, config.width * config.height / 80000]);


    // SR: ok. here's something stupid: each node consists of 4 element:
    // - a background rect with stroke to outline the label
    // - a circle for the node (with stroke)
    // - a foreground rect, exactly like the background rect, except no stroke
    // - a text element with the name
    // the foreground rect is there so the stroke from the circle that would overlap with the text
    // is hidden.
    nodes
        .append('rect')
            .attr('class', 'node_label_rect_background')
            .attr('visibility', (d) => d.visibility );

    nodes.append("circle")
        .attr("r", (d) => {
            let circle_radius;
            if (d.degree === 1){
                circle_radius = node_size_scale_degree_1(d.docs)
            } else {
                circle_radius = node_size_scale_degree_2(d.docs)
            }
            d.circle_radius = circle_radius;
            return circle_radius;
        })
        .attr("x", (d) => data.clusters[d.cluster]['x_pos'])
        .attr("y", (d) => data.clusters[d.cluster]['y_pos'])
        .attr('class', (d) => `node degree_${d.degree}` )
        .attr('fill', (d) =>{
            if (d.degree === 1){
                return d3.interpolateLab('white', data.clusters[d.cluster].color)(0.3)
            } else {
                return data.clusters[d.cluster].color
            }
        })
        .attr('stroke', (d) => {
            if (d.degree === 1){
                return data.clusters[d.cluster].color
            } else {
                return '#f2f2f3'
            }
        });

    nodes
        .append('rect')
            .attr('class', 'node_label_rect_foreground')
            .attr('visibility', (d) => d.visibility );

    nodes
        .append("text")
            .text((d) => d.name)
            .style("fill", "#555")
            .style("font-family", "Arial")
            .style("font-size", 12)
            .attr("text-anchor", "middle")
            .attr('alignment-baseline', 'central')
            .attr('transform', (d) => {
                if (d.degree === 1) {
                    return 'translate(0, 0)'
                } else {
                    return 'translate(0, -20)'
                }
            })
            // .attr("transform", (d, i, n) => calc_label_pos(d, i, n))
            .style("pointer-events", "none")
            .attr('visibility', (d) => d.visibility );

    nodes.selectAll('rect')
        .attr('rx', 3)
        .attr('ry', 3)
        .attr('x', (_, i, n) => {
            // select the parent of the i-th node, which is the parent node group
            const parent_node_group = d3.select(n[i].parentNode);
            // then, get the bounding box of the text child element
            // TODO: figure out a better way of getting the bbox.
            const text_bbox = parent_node_group.selectAll('text').node().getBBox();
            return text_bbox.x - 2
        })
        .attr('y', (d, i, n) => {
            // now as an ugly oneliner
            let y_pos = d3.select(n[i].parentNode).selectAll('text').node().getBBox().y - 2;
            // 2nd degree labels should be above the node, not on the node
            if (d.degree !== 1){
                y_pos -= 20
            }
            return y_pos
        })
        .attr('width', (_, i, n) => {
            // now as an ugly oneliner
            return d3.select(n[i].parentNode).selectAll('text').node().getBBox().width + 4
        })
        .attr('height', (_, i, n) => {
            // now as an ugly oneliner
            return d3.select(n[i].parentNode).selectAll('text').node().getBBox().height + 4
        })

        .attr('fill', (d) => d3.interpolateLab('white', data.clusters[d.cluster].color)(0.3));

    nodes.selectAll('.node_label_rect_background')
        .attr('stroke', (d) => data.clusters[d.cluster].color);




    // // Setup labels
    // const calc_label_pos = (d, i, nodes) => {
    //     const label = nodes[i];
    //     const r = node_size_scale(d.docs);
    //     const h = label.getBBox().height;  // bounding box of the label
    //     const w = label.getBBox().width;
    //     // TODO: adjust position of the label based on radius of the circle
    //     const shiftX = -w/2;
    //     const shiftY = -h/2-r;
    //     return `translate(${shiftX}, ${shiftY})`;
    // };



    clusters.append('text')
        .text((d) => d.name)
        .style('fill', (d) => d.color)
        .style('font-size', (config.width - 50) * config.height / 50000 )
        .attr("text-anchor", "middle")
        .attr("x", (d) => (d.x_pos + 0.2) * config.width / 3 * 2)
        .attr("y", (d) => (d.y_pos + 0.2) * config.height / 3 * 2);

    // clusters.append('circle')
    //     .style('fill', (d) => d.color)
    //     .attr('cx', (d) => (d.x_pos + 0.2) * config.width / 3 * 2)
    //     .attr('cy', (d) => (d.y_pos + 0.2) * config.height / 3 * 2)
    //     .attr('r', 20);

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
    // function resize() {
    //     const width = window.innerWidth;
    //     const height = window.innerHeight;
    //
    //     svg.attr("width", width).attr("height", height);
    //     config.width = width;
    //     config.height = height;
    //     let force_simulation = initialize_force_sim(config, data);
    //     force_simulation.alphaTarget(0.3).restart();
    //     force_simulation.alphaTarget(0);
    // }



    // d3.select(window).on("resize", resize);

    // send databindings back to react so they can be used later to update the chart
    data_bindings = {
        'svg': svg,
        'nodes': nodes,
        'links': links,
        'clusters': clusters
    };
    handle_viz_events('update_data_bindings', data_bindings);

    nodes  // bind event handlers for nodes
        .call(
            d3.drag()
                .on("start", (d) => {
                    data_bindings.nodes.on("mouseover", () => {}).on("mouseout", () => {});
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on("drag", (d) => {
                    d.x = d3.event.x;
                    d.y = d3.event.y;
                    render_simulation(config, data, data_bindings);
                })
                .on("end", (d) => {
                    d.x = d3.event.x;
                    d.y = d3.event.y;
                    render_simulation(config, data, data_bindings);
                    data_bindings.nodes
                        .on("mouseover", (d) => handle_viz_events('mouseover', d))
                        .on("mouseout", (d) => handle_viz_events('mouseout', d))
                })
        )
        .on("mouseover", (d) => handle_viz_events('mouseover', d))
        .on("mouseout", (d) => handle_viz_events('mouseout', d))
        .on("click", (d, _i) => handle_viz_events('click', d));


    // Initialize the force simulation - see https://github.com/d3/d3-force
    // This creates the x and y values for the data, based on relationships here
    // n.b. this doesn't actually render the sim - we do that below
    // by adding nodes to the svg and updating their position in render_simulation


    // run 400 ticks before displaying the result. That way, the simulation is mostly settled
    // but still slightly moving.
    for (let i = 0; i < 400; i++){
        force_simulation.tick(1);

        // SR: I don't know why x/y/vx/vy sometimes get into the millions.
        // These extreme values lead to page freezes. By capping these attributes, the freezes
        // can be prevented.
        data_bindings.nodes.each((d) => {
            if (d.vx > 1000){
                d.vx = 1000
            } else if (d.vx < -1000){
                d.vx = -1000
            }
            if (d.vy > 1000){
                d.vy = 1000
            } else if (d.vy < -1000){
                d.vy = -1000
            }
            if (d.x > 3000) {
                d.x = 3000
            } else if (d.x < -3000) {
                d.x = -3000
            }
            if (d.y > 3000){
                d.y = 3000
            } else if (d.y < -3000){
                d.y = -3000
            }
        })
    }
}


function force_sim(config,data) {
    const force_x_pos = (d) => {
        if (d.has_been_dragged) {
            return d.x_grav;
        } else {
            return get_gravity_center(d, config, data)[0];
        }
    };
    const force_y_pos = (d) => {
        if (d.has_been_dragged) {
            return d.y_grav;
        } else {
            return get_gravity_center(d, config, data)[1];
        }
    };
    const cluster_strength = (d) => {
        if (d.has_been_dragged){
            return 3;
        } else {
            return 1;
        }
    };

    let force_simulation = d3.forceSimulation(data.nodes);
    force_simulation
        .force("charge", d3.forceManyBody())
        .force('collision', d3.forceCollide().radius(30))
        .force('x', d3.forceX()
            .x((d) => force_x_pos(d))
            .strength(cluster_strength)
        )
        .force('y', d3.forceY().y((d) => force_y_pos(d)).strength(cluster_strength))
        .force('center', d3.forceCenter(config.width / 2, config.height / 2).strength(2000))
        .on("tick", () => render_simulation(config, data));  // what to do when the sim updates
    }

function get_gravity_center(d, config, data){

    // if clustering inactive -> all nodes in the center of the graph
    if (!config.cluster_nodes){
        return [config.width / 2, config.height /2]
    } else {
        const x_pos = (data.clusters[d.cluster]['x_pos'] + 0.2) * config.width / 3 * 2;
        const y_pos = (data.clusters[d.cluster]['y_pos'] + 0.2) * config.height / 3 * 2;
        return [x_pos, y_pos]
    }
}

/*
 * Event handlers
 */
// Update the position of all svg elements according to the force sim
// This function is called whenever the simulation updates
// eslint-disable-next-line no-unused-vars
function render_simulation(config, data, data_bindings) {

    // Update node positions
    data_bindings.nodes.attr("transform", (d) => {
        d.x = Math.max(d.circle_radius, Math.min(config.width - d.circle_radius, d.x));
        d.y = Math.max(d.circle_radius, Math.min(config.height - d.circle_radius, d.y));
        return `translate(${d.x}, ${d.y})`
    } );

    // Update link positions
    data_bindings.links
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

    // the annoying part: reset the cluster labels to the center of each cluster
    // (the clusters move with the layout -> they change after a few seconds of applied force)

    // first, add current x and y values for each node to a dict with the clusters
    let cluster_centers = {};
    data_bindings.nodes.each((d) => {
        if (!(d.cluster in cluster_centers)){
            cluster_centers[d.cluster] = {
                'x_pos': [],
                'y_pos': []
            }
        }
        cluster_centers[d.cluster]['x_pos'].push(d.x);
        cluster_centers[d.cluster]['y_pos'].push(d.y);
    });


    // then calculate the center of each cluster and move the text to the new center
    data_bindings.clusters.selectAll('text')
        .attr('x', (d) => {
            return d3.mean(cluster_centers[d.id]['x_pos'])
        })
        .attr('y', (d) => d3.mean(cluster_centers[d.id]['y_pos']));

    const link_width_scale_degree_1 = d3.scaleLinear()
        .domain([0, d3.max(data['links'], function(d) { return d.docs})])
        .range([2, 3]);
    const link_width_scale_degree_2 = d3.scaleLinear()
        .domain([0, d3.max(data['links'], function(d) { return d.docs})])
        .range([0.5, 2]);

    data_bindings.links
        .attr("class", (d) => `graph_link degree_${d.degree}`)
        .attr("stroke-width", (d) => {
            if (d.degree === 1){
                return link_width_scale_degree_1(d.docs);
            } else {
                return link_width_scale_degree_2(d.docs);
            }
        })
        .attr('visibility', (d) => d.visibility);

    // const max_docs = d3.max(data['nodes'], function(d) { return d.docs; });
    // const node_size_scale_degree_1 = d3.scaleLinear()
    //     .domain([0, max_docs])
    //     .range([20, config.width * config.height / 60000]);
    // const node_size_scale_degree_2 = d3.scaleLinear()
    //     .domain([0, max_docs])
    //     .range([5, config.width * config.height / 80000]);

    data_bindings.nodes.selectAll('rect,text')
        .attr('visibility', (d) => d.visibility );

}

function initialize_force_sim(config, data, data_bindings) {

    //re-init from graph initialization because it somehow didn't get to this function
    const max_docs = d3.max(data['nodes'], function(d) { return d.docs; });
    const node_size_scale = d3.scaleLinear()
        .domain([0, max_docs])
        .range([5, config.width * config.height / 80000]);

    const force_x_pos = (d) => {
        return get_gravity_center(d, config, data)[0];
    };
    const force_y_pos = (d) => {
        return get_gravity_center(d, config, data)[1];
    };

    const cluster_strength = 5;

    const link_strength_scale = d3.scaleLinear()
        .domain([0, d3.max(data['links'], function(d) { return d.docs})])
        .range([0, 5]);

    let force_simulation = d3.forceSimulation(data.nodes);
    force_simulation
        .force('x', d3.forceX()
                        .x(force_x_pos)
                        .strength(cluster_strength))
        .force('y', d3.forceY()
                        .y(force_y_pos)
                        .strength(cluster_strength))

        .force("center", d3.forceCenter().x(config.width / 2).y(config.height / 2))

        // the most central nodes should be dragged towards the center
        // one way of accomplishing this is to have an attraction between nodes based on the
        // number of documents that they have exchanged IF they are in different clusters
        .force("links",
            d3.forceLink(data.links)
                .strength(function (d) {
                    if (d.source.cluster === d.target.cluster){
                        return link_strength_scale(d.docs) / 5000
                    } else {
                        return link_strength_scale(d.docs)
                    }
                })
                .id((d) => d.name)  // which data field to use as id for links
        )

        .force('avoid_node_collisions', d3.forceCollide()
            .radius((d) => {
                // make sure that at least 50% of the svg space is unoccupied by nodes
                // each node takes up PI * r^2
                // -> PI * r^2 * no_nodes * 2 < height * width
                return d3.min([
                    node_size_scale(d.docs) + 30,
                    Math.sqrt(config.width * config.height / data.nodes.length / Math.PI / 2)
                    ])
            })
        )
        // how fast energy in the system should decay. Default: 0.0228
        .alphaDecay(0.01)
        // basically a friction parameter. Default: 0.4
        .velocityDecay(0.8)
        .on("tick",() => {
            return render_simulation(config, data, data_bindings)
        });  // what to do when the sim updates

    return force_simulation;
}

function change_clusters(config, data) {
    force_sim(config,data);
    function resize() {
        const svg = d3.select("#graph_svg");
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

    // let force_simulation = d3.forceSimulation(data.nodes);

    // const all_graph_nodes = d3.select("#graph_nodes");
    // const nodes = all_graph_nodes.selectAll('g');

    // const all_graph_links = d3.select("#graph_links");
    // const links = all_graph_links.selectAll('line');
    // nodes  // bind event handlers for nodes
    //     .call(
    //         d3.drag()
    //             .on("start", (d) => drag_started(d,nodes,force_simulation))
    //             .on("drag", (d) => dragged(d))
    //             .on("end", (d) => drag_ended(d,config,data,nodes,links,force_simulation))
    //     )
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
 * @param el: the html element to which the graph is bound
 * @param data: data
 * @param config: the graph config from react
 * @param action: the update action, e.g. "focus" or "cluster_nodes"
 */
export function update_graph(el, data, config, data_bindings, action) {
    if (action === 'update_focus') {

        console.log("update focus");

        const link_width_scale_degree_1 = d3.scaleLinear()
            .domain([0, d3.max(data['links'], function(d) { return d.docs})])
            .range([2, 3]);
        const link_width_scale_degree_2 = d3.scaleLinear()
            .domain([0, d3.max(data['links'], function(d) { return d.docs})])
            .range([0.5, 2]);
        data_bindings.links.transition('link_strokes').duration(1000)
            .attr("stroke-width", (d) => {
                if (d.degree === 1){
                    return link_width_scale_degree_1(d.docs);
                } else {
                    return link_width_scale_degree_2(d.docs);
                }
            });
        data_bindings.links
            .attr("class", (d) => `graph_link degree_${d.degree}`);

        data_bindings.nodes.selectAll('rect,text').transition('node_labels').duration(1000)
            .attr('visibility', (d) => d.visibility );


//        render_simulation(config, data, data_bindings);

        // const max_docs = d3.max(data['nodes'], function(d) { return d.docs; });
        // const node_size_scale = d3.scaleLinear()
        //     .domain([0, max_docs])
        //     .range([5, config.width * config.height / 80000]);
        //
        // data_bindings.nodes
        //     .style('opacity', (d) =>{
        //     //data_bindings.nodes.style('opacity', (d) => {
        //     if (d.degree === -1){ return 0 } else { return 1}
        // });

        // data_bindings.nodes.selectAll('circle')
        //     .attr('class', (d) => `node_degree_${d.degree}`);

        // data_bindings.nodes.selectAll('circle').transition().duration(1000)
        //     .attr('r', (d) => {
        //         let radius = node_size_scale(d.docs);
        //         if (d.degree === 0) { return 20} else {return radius}
        //     })
        //     .attr('class', (d) => `node degree_${d.degree}`)
        //
        //     .attr('fill', (d) => {
        //         if(d.degree === 0 || d.degree === 1){
        //             return data.clusters[d.cluster].color
        //         } else {
        //             return 'white'
        //         }
        //     })
        //     .attr('stroke', (d) =>{
        //         if(d.degree === 0 || d.degree === 1){
        //             return 'white'
        //         } else {
        //             return data.clusters[d.cluster].color
        //         }
        //     });




        // data_bindings.links.transition().duration(500).style('opacity', (d) =>{
        //     if (d.degree === -1){return 0 } else {return 1}
        // });

        // update_focused_node(el, data, config, data_bindings);
    } else if (action === "cluster_nodes") {
        // initialize_force_sim(config, data);
        change_clusters(config, data);
    } else {
        //function update_unfocus_node (el, data, config) {
        const svg = d3.select(el);
        svg.selectAll(".graph_node").style("opacity", 1);
        svg.selectAll(".graph_link").style("opacity", 1);
    }
}


