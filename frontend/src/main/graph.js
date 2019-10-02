/**
 * Graph code mostly in D3 for the visualization
 */
import * as d3 from 'd3';


/**
 * Create a graph for d3
 *
 * @param el: Node
 * @param data: object[]
 * @param config: object
 * @param handle_viz_events: Function
 */
export function create_graph(el, data, config, handle_viz_events) {
    d3.select(el)
        .append('svg')
        .attr('width', config.width)
        .attr('height', config.height)
        .selectAll('rect')
        .data(data['nodes'])
        .enter()
        .append('rect')
        .attr('x', (d, _i) => _i * 10)
        .attr('y', (d) => config.height - d.docs / 25)
        .attr('width', 9)
        .attr('height', (d) => d.docs / 25)
        .attr('fill', config.color)
        .on('mouseover', (node_data,_i) => handle_viz_events('mouseover', node_data))
        .on('mouseout',  (node_data,_i) => handle_viz_events('mouseout', node_data))
        .on('click', (node_data, _i)    => handle_viz_events('click', node_data))
    ;
}


/**
 * Change the color of each of the rectangles in the graph, slowly.
 *
 * @param el: Node
 * @param data: object[]
 * @param config: object
 */
export function update_graph_color(el, data, config) {
    // D3 Code to update the chart
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

