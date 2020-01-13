export function update_node_degree_and_visibility(data, config, center_node_name) {
    console.log(center_node_name)
    if (center_node_name === undefined){
        data
    }


    data = update_node_degree(data, center_node_name);
    data = update_node_visibility(data, config.selected_viz_degree, center_node_name);


    return data

}



function update_node_degree(data, center_node_name){

    let center_names = {... data.center_names};
    console.log(center_names)
    if (center_node_name !== undefined){
        center_names[center_node_name] = true
    }

    // first, set all degrees to 2
    data.nodes.forEach((d) => {
        d.degree = 2;
    });
    data.links.forEach((d) => {
        d.degree = 3;
    });

    data.links.forEach((d) => {
        if (d.source.name in center_names) {
            d.degree = 2;
            d.source.degree = 1;
            if (d.target.name in center_names) {
                d.target.degree = 1;
                d.degree = 1;
            }
        } else if (d.target.name in center_names) {
            d.target.degree = 1;
            d.degree = 2;
        }

        if (d.source.name === center_node_name || d.target.name === center_node_name){
            d.degree = 1;
        }
    });

    data.links.sort((a, b) => a.degree - b.degree);

    // if (center_node_name !== undefined) {
    //     data.links.forEach((d) => {
    //         if (d.source.name !== center_node_name && d.target.name !== center_node_name) {
    //             d.degree = -1;
    //             d.source.degree = -1;
    //             d.target.degree = -1;
    //         }
    //     });
    // }

    //TODO: Handle visibility separate from degree

    return data
}

function update_node_visibility(data, viz_degree, center_node_name){


    data.nodes.forEach((d) => {

        if (d.degree <= 1){
            d.visibility = 'visible'
        } else {
            d.visibility = 'hidden'
        }
    });
    data.links.forEach((d) => {
        if (d.degree <= viz_degree * 2){
            d.visibility = 'visible'
        } else {
            d.visibility = 'hidden'
        }

        if (d.source.name === center_node_name || d.target.name === center_node_name){
            d.source.visibility = 'visible';
            d.target.visibility = 'visible';
        }
    });

    return data

}
