import React from 'react';
import MainLayout from "./main_layout";
import MainView from "./main";
//import PropTypes from 'prop-types';


export class NetworkExplorationView extends React.Component{
    constructor(props){
        super(props);
    }

    render(){
        return(
            <>
                <div className='row'>
                    <div className='col-12'>


                        <MainLayout
                            content={
                                <div id={"main_body"}>
                                    <MainView
                                        show_dataset_selector={true}
                                        element_for_graph_sizing='main_body'
                                    />
                                </div>
                            }
                        />
                    </div>;
                </div>
            </>
        )
    }
}

// NetworkExplorationView.propTypes={
//     dataset_name: PropTypes.string.isRequired,
// }

export default NetworkExplorationView;

