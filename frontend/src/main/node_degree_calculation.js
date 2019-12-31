export function update_node_degrees(data, center_node_name){

    console.log("Update degree", center_node_name);

    // if center_node_name is undefined (no center node), set all node and link degrees
    // to -1

    let default_value = 3;

    if (center_node_name === undefined) {
        default_value = -1
    }
    data.nodes.forEach((d) => {
        d.degree = default_value;
    });
    data.links.forEach((d) => {
        d.degree = default_value;
    });


    if (center_node_name !== undefined){
        data.links.forEach((d) => {
            if (center_node_name === d.source.name){
                d.source.degree = 0;
                d.target.degree = 1;
                d.degree = 1;
            } else if (center_node_name === d.target.name){
                d.target.degree = 0;
                d.source.degree = 1;
                d.degree = 1;
            }
        })

    }

    return data
}
