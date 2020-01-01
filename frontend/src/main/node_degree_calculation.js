export function update_node_degrees(data, center_node_name){

    console.log("Update degree", center_node_name);
    console.log(data.center_names);

    // if center_node_name is undefined (no center node), set all node and link degrees
    // to -1



    let default_value = 2;

    data.nodes.forEach((d) => {
        d.degree = default_value;
    });
    data.links.forEach((d) => {
        d.degree = default_value;
    });


    // if (center_node_name !== undefined){

    data.links.forEach((d) => {
        // if (center_node_name === d.source.name){
        // There has to be a better way to check if an object has a key.
        if (d.source.name in data.center_names){
            d.degree = 1;
            d.source.degree = 1;
            d.target.degree = 2;
            if (d.target.name in data.center_names) {
                d.target.degree = 1;
            }
        } else if (d.target.name in data.center_names) {
            d.target.degree = 1;
            d.source.degree = 2;
            d.degree = 1;
        }
    });

    if (center_node_name !== undefined) {
        data.links.forEach((d) => {
            if (d.source.name !== center_node_name && d.target.name !== center_node_name) {
                d.degree = -1;
                d.source.degree = -1;
                d.target.degree = -1;
            }
        });
    }

    //TODO: Handle visibility separate from degree

    return data
}
