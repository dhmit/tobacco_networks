/**
 * Graph code mostly in D3 for the visualization
 */
import * as d3 from 'd3';


export function create_graph(el, data, config, handle_viz_events) {
    d3.select(el)
        .append("svg")
        .attr("width", config.width)
        .attr("height", config.height)
        .selectAll("rect")
        .data(data.values)
        .enter()
        .append("rect")
        .attr("x", (d, i) => i * 70)
        .attr("y", (d, _i) => config.height - 10 * d)
        .attr("width", 65)
        .attr("height", (d, _i) => d * 10)
        .attr("fill", config.color)
        .attr("fill", config.color)
        .on("mouseover", (_d,_i) => handle_viz_events("mouseover"))
        .on("mouseout",  (_d,_i) => handle_viz_events("mouseout"))
        .on("click", () => handle_viz_events("click"))
    ;
}


export function update_graph_color(el, data, config) {
    // D3 Code to update the chart
    // Re-compute the scales, and render the data points
    d3.select(el).selectAll("rect")
        .transition()
        .duration(1000)
        .style("fill", config.color)
}

/*
 * TODO:
 *   - destroy and recreate graph with new data
 *   - some kind of hooks to call different updates; e.g.,
 *     - filtering by topic
 *     -
 *
 */

